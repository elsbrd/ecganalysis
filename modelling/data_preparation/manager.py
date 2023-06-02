import logging
import os
import pickle
import random
from collections import Counter

import joblib
import numpy as np
import wfdb
from biosppy.signals import ecg
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from modelling.constants import (
    MITDB,
    MITDB_DATASET_DIR,
    MITDB_FEATURES_DIR,
    SCALER_MODELS_CACHE_DIR,
)
from modelling.data_preparation.utils import extract_wave_features

logger = logging.getLogger("ecg_analysis")


class MITDBDatasetManager:
    def download_dataset(self):
        if not self._is_dataset_downloaded():
            logger.info("MIT dataset is not found. Starting the download process...")

            wfdb.dl_database(MITDB, MITDB_DATASET_DIR)

    def get_records_and_annotations(self):
        self.download_dataset()

        records, annotations = [], []

        for i in self._get_indices():
            kwargs = {"record_name": f"{MITDB_DATASET_DIR}/{i}", "sampto": 500000}

            record = wfdb.rdsamp(**kwargs)
            annotation = wfdb.rdann(**kwargs, extension="atr")

            records.append(record)
            annotations.append(annotation)

        return records, annotations

    def extract_heartbeats_and_waves_from_records(self, records, annotations):
        heartbeats = []
        heartbeat_annotations = []

        p_waves = []
        qrs_complexes = []
        t_waves = []

        for record, annotation in tqdm(
            zip(records, annotations),
            total=len(records),
            desc="Extracting heartbeats, heartbeat annotations and P/QRS/T waves...",
        ):
            fs = record[1]["fs"]

            ecg_signal = record[0][:, 1]
            signal_len = len(ecg_signal)

            out = ecg.ecg(signal=ecg_signal, sampling_rate=fs, show=False)
            rpeaks = out["rpeaks"]
            rr_intervals = np.diff(rpeaks)
            average_rr_interval = np.mean(rr_intervals)

            samples = annotation.sample
            symbols = annotation.symbol

            for r_peak in rpeaks:
                # define the start and end of a heartbeat
                start, end = (
                    max(int(r_peak - average_rr_interval * 0.3), 0),
                    min(int(r_peak + average_rr_interval * 0.5), signal_len - 1),
                )

                # calculate boundaries for annotations
                lower_bound, upper_bound = (
                    max(r_peak - average_rr_interval * 0.2, start),
                    min(r_peak + average_rr_interval * 0.2, end),
                )

                # find indices of annotations within boundaries
                annotation_indices = np.where(
                    (samples >= lower_bound) & (samples <= upper_bound)
                )[0]

                # skip if there are no annotations in the range
                if len(annotation_indices) == 0:
                    continue

                # find the closest annotation to the r peak
                closest_annotated_r_peak = annotation_indices[
                    np.argmin(np.abs(samples[annotation_indices] - r_peak))
                ]

                heartbeat = ecg_signal[start:end]

                # Skip '+' annotations
                heartbeat_annotation = symbols[closest_annotated_r_peak]
                if heartbeat_annotation == "+":
                    continue

                # Skip heartbeats below a certain length threshold
                if len(heartbeat) < average_rr_interval * 0.5:
                    continue

                # Append the heartbeat and corresponding annotation
                heartbeats.append(heartbeat)
                heartbeat_annotations.append(heartbeat_annotation)

                # Simple approach to extract P-waves, QRS complexes, and T-waves in the range of the heartbeat
                p_wave_end = start + int((end - start) * 0.2)
                qrs_complex_end = p_wave_end + int((end - start) * 0.4)

                p_wave = ecg_signal[start:p_wave_end]
                qrs_complex = ecg_signal[p_wave_end:qrs_complex_end]
                t_wave = ecg_signal[qrs_complex_end:end]

                p_waves.append(p_wave)
                qrs_complexes.append(qrs_complex)
                t_waves.append(t_wave)

        return heartbeats, heartbeat_annotations, p_waves, qrs_complexes, t_waves

    def balance_heartbeats_and_waves(
        self, heartbeats, heartbeat_annotations, p_waves, qrs_complexes, t_waves
    ):
        # Get the counter of the annotations
        counter = Counter(heartbeat_annotations)

        # Find classes with count < 75
        low_count_classes = [k for k, v in counter.items() if v < 75]

        # Downsample 'N' class to the count of 'L' class
        downsampled_N = random.sample(
            [
                i
                for i in range(len(heartbeat_annotations))
                if heartbeat_annotations[i] == "N"
            ],
            counter["L"],
        )

        indices_to_keep = downsampled_N + [
            i
            for i in range(len(heartbeat_annotations))
            if heartbeat_annotations[i] not in ["N"] + low_count_classes
        ]

        # Create balanced data
        balanced_heartbeats = [heartbeats[i] for i in indices_to_keep]
        balanced_annotations = [heartbeat_annotations[i] for i in indices_to_keep]
        balanced_p_waves = [p_waves[i] for i in indices_to_keep]
        balanced_qrs_complexes = [qrs_complexes[i] for i in indices_to_keep]
        balanced_t_waves = [t_waves[i] for i in indices_to_keep]

        return (
            balanced_heartbeats,
            balanced_annotations,
            balanced_p_waves,
            balanced_qrs_complexes,
            balanced_t_waves,
        )

    def scale_wave_features(
        self, p_wave_features, qrs_complex_features, t_wave_features
    ):
        scaler_p = StandardScaler()
        scaler_qrs = StandardScaler()
        scaler_t = StandardScaler()

        p_wave_features_scaled = scaler_p.fit_transform(p_wave_features)
        qrs_complex_features_scaled = scaler_qrs.fit_transform(qrs_complex_features)
        t_wave_features_scaled = scaler_t.fit_transform(t_wave_features)

        return (
            p_wave_features_scaled,
            qrs_complex_features_scaled,
            t_wave_features_scaled,
            scaler_p,
            scaler_qrs,
            scaler_t,
        )

    def cache_scalers(
        self,
        scaler_p,
        scaler_qrs,
        scaler_t,
    ):
        scalers = {
            "scaler_p": scaler_p,
            "scaler_qrs": scaler_qrs,
            "scaler_t": scaler_t,
        }

        for name, scaler in scalers.items():
            joblib.dump(scaler, os.path.join(SCALER_MODELS_CACHE_DIR, f"{name}.pkl"))

    def cache_wave_features_and_annotations(
        self,
        p_wave_features,
        qrs_complex_features,
        t_wave_features,
        heartbeat_annotations,
    ):
        features = {
            "p_wave": p_wave_features,
            "qrs_complex": qrs_complex_features,
            "t_wave": t_wave_features,
            "heartbeat_annotations": heartbeat_annotations,
        }

        for name, feature in features.items():
            with open(os.path.join(MITDB_FEATURES_DIR, f"{name}.pkl"), "wb") as f:
                pickle.dump(feature, f)

    def cache_features(self):
        records, annotations = self.get_records_and_annotations()
        logger.info(
            "MIT dataset records and annotations have been successfully gathered."
        )

        (
            heartbeats,
            heartbeat_annotations,
            p_waves,
            qrs_complexes,
            t_waves,
        ) = self.extract_heartbeats_and_waves_from_records(records, annotations)
        logger.info(
            "MIT dataset heartbeats, heartbeat waves, corresponding annotations have been successfully extracted."
        )

        (
            heartbeats,
            heartbeat_annotations,
            p_waves,
            qrs_complexes,
            t_waves,
        ) = self.balance_heartbeats_and_waves(
            heartbeats,
            heartbeat_annotations,
            p_waves,
            qrs_complexes,
            t_waves,
        )
        logger.info("MIT dataset has been successfully balanced.")

        (
            p_wave_features,
            qrs_complex_features,
            t_wave_features,
        ) = extract_wave_features(p_waves, qrs_complexes, t_waves)
        logger.info(
            "MIT dataset heartbeat wave features have been successfully extracted."
        )

        (
            p_wave_features_scaled,
            qrs_complex_features_scaled,
            t_wave_features_scaled,
            scaler_p,
            scaler_qrs,
            scaler_t,
        ) = self.scale_wave_features(
            p_wave_features, qrs_complex_features, t_wave_features
        )
        logger.info(
            "MIT dataset heartbeat wave features have been successfully scaled."
        )

        self.cache_scalers(
            scaler_p,
            scaler_qrs,
            scaler_t,
        )
        logger.info(
            "StandardScaler() objects for heartbeat wave features have been successfully saved."
        )

        self.cache_wave_features_and_annotations(
            p_wave_features_scaled,
            qrs_complex_features_scaled,
            t_wave_features_scaled,
            heartbeat_annotations,
        )
        logger.info("MIT dataset features and annotations were successfully cached.")

    def load_scalers_from_cache(self):
        return (
            joblib.load(
                os.path.join(os.path.join(SCALER_MODELS_CACHE_DIR, "scaler_p.pkl"))
            ),
            joblib.load(
                os.path.join(os.path.join(SCALER_MODELS_CACHE_DIR, "scaler_qrs.pkl"))
            ),
            joblib.load(
                os.path.join(os.path.join(SCALER_MODELS_CACHE_DIR, "scaler_t.pkl"))
            ),
        )

    def load_features_and_annotations_from_cache(self):
        with open(os.path.join(MITDB_FEATURES_DIR, "p_wave.pkl"), "rb") as f:
            p_wave_features = pickle.load(f)  # nosec

        with open(os.path.join(MITDB_FEATURES_DIR, "qrs_complex.pkl"), "rb") as f:
            qrs_complex_features = pickle.load(f)  # nosec

        with open(os.path.join(MITDB_FEATURES_DIR, "t_wave.pkl"), "rb") as f:
            t_wave_features = pickle.load(f)  # nosec

        with open(
            os.path.join(MITDB_FEATURES_DIR, "heartbeat_annotations.pkl"), "rb"
        ) as f:
            heartbeat_annotations = pickle.load(f)  # nosec

        return (
            p_wave_features,
            qrs_complex_features,
            t_wave_features,
            heartbeat_annotations,
        )

    def _is_dataset_downloaded(self):
        return os.path.isdir(MITDB_DATASET_DIR) and len(os.listdir(MITDB_DATASET_DIR))

    def _get_indices(self):
        return wfdb.get_record_list(MITDB)
