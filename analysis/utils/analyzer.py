import numpy as np
import pandas as pd
import plotly.graph_objects as go

from analysis.constants import HEARTBEAT_LABEL_VERBOSE
from analysis.utils.functions import extract_heartbeats_and_waves
from modelling.data_preparation.manager import MITDBDatasetManager
from modelling.data_preparation.utils import (
    concatenate_letters,
    convert_labels_to_letters,
    extract_wave_features,
)


class ECGAnalyzer:
    def __init__(self, analysis_session, training_session):
        self._analysis_session = analysis_session
        self._training_session = training_session

    def get_analysis_result(self):
        df = pd.read_csv(self._analysis_session.ecg_file)
        ecg_signal = df["signal"].values

        (
            heartbeat_intervals,
            p_wave_features_scaled,
            qrs_complex_features_scaled,
            t_wave_features_scaled,
        ) = self._prepare_features(ecg_signal)

        words = self._generate_words(
            p_wave_features_scaled, qrs_complex_features_scaled, t_wave_features_scaled
        )

        vectors = self._generate_vectors(words)

        predicted_labels = self._predict_labels(vectors)

        chart = self.__plot_ecg_with_annotations(
            ecg_signal, heartbeat_intervals, predicted_labels
        )

        return {
            "charts": {"line": chart},
            "table": self.__generate_heartbeats_table_data(
                predicted_labels, words, vectors
            ),
        }


    def _prepare_features(self, ecg_signal):
        (
            heartbeats,
            heartbeat_intervals,
            p_waves,
            qrs_complexes,
            t_waves,
        ) = extract_heartbeats_and_waves(ecg_signal, fs=self._analysis_session.fs)

        p_wave_features, qrs_complex_features, t_wave_features = extract_wave_features(
            p_waves, qrs_complexes, t_waves
        )

        dataset_manager = MITDBDatasetManager()
        scaler_p, scaler_qrs, scaler_t = dataset_manager.load_scalers_from_cache()

        p_wave_features_scaled = scaler_p.transform(p_wave_features)
        qrs_complex_features_scaled = scaler_qrs.transform(qrs_complex_features)
        t_wave_features_scaled = scaler_t.transform(t_wave_features)
        return (
            heartbeat_intervals,
            p_wave_features_scaled,
            qrs_complex_features_scaled,
            t_wave_features_scaled,
        )

    def _generate_words(self, p_wave_features, qrs_complex_features, t_wave_features):
        kmeans_p, kmeans_qrs, kmeans_t = self._training_session.get_kmeans_models()

        labels_p = kmeans_p.predict(p_wave_features)
        labels_qrs = kmeans_qrs.predict(qrs_complex_features)
        labels_t = kmeans_t.predict(t_wave_features)

        letters_p = convert_labels_to_letters(labels_p)
        letters_qrs = convert_labels_to_letters(labels_qrs)
        letters_t = convert_labels_to_letters(labels_t)

        heartbeat_words = concatenate_letters(letters_p, letters_qrs, letters_t)
        return heartbeat_words

    def _generate_vectors(self, words):
        word2vec = self._training_session.get_word2vec_model()

        def word_to_vec(word):
            return np.mean([word2vec.wv[letter] for letter in word], axis=0)

        word_vectors = [word_to_vec(w) for w in words]
        return word_vectors

    def _predict_labels(self, vectors):
        classifier = self._training_session.get_classifier_model()

        predicted_labels = [classifier.predict(f.reshape(1, -1)) for f in vectors]
        predicted_labels_expanded = [
            HEARTBEAT_LABEL_VERBOSE[label[0]] for label in predicted_labels
        ]

        return predicted_labels_expanded

    @staticmethod
    def __plot_ecg_with_annotations(
        ecg_signal, heartbeat_intervals, predicted_labels_expanded
    ):
        # create the figure
        fig = go.Figure()

        # add entire ECG signal trace as a gray dotted line
        fig.add_trace(
            go.Scatter(
                x=list(range(len(ecg_signal))),
                y=ecg_signal,
                mode="lines",
                line=dict(color="lightgrey"),  # make this line dotted
                hoverinfo="none",  # no hover info for this trace
                showlegend=False,  # do not show this trace in the legend
            )
        )

        # iterate through heartbeat intervals and predicted labels
        for i, interval in enumerate(heartbeat_intervals):
            start, end = interval
            segment = ecg_signal[start:end]
            label = predicted_labels_expanded[i]

            # set the line color based on the label
            line_color = "#008000" if label.lower() == "normal beat" else "#800000"

            # add this segment as a new trace to the figure
            fig.add_trace(
                go.Scatter(
                    x=list(range(start, end)),
                    y=segment,
                    mode="lines",
                    line=dict(color=line_color, width=2),
                    hoverinfo="text",
                    hovertext=label,
                    showlegend=False,
                )
            )

        # add rangeslider to the xaxis configuration
        fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True), type="linear"),
            showlegend=True,
            autosize=True,
            title=None,
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return fig.to_json()

    @staticmethod
    def __generate_heartbeats_table_data(
        predicted_labels_expanded, heartbeat_words, features
    ):
        return [
            {
                "index": i + 1,
                "predicted_label": predicted_labels_expanded[i],
                "word": heartbeat_words[i],
                "word_vector": features[i],
            }
            for i in range(min(20, len(predicted_labels_expanded)))
        ]
