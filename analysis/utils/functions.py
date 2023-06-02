import numpy as np

from biosppy.signals import ecg


def extract_heartbeats_and_waves(ecg_signal, fs: int = 360):
    heartbeats = []
    heartbeat_intervals = []

    p_waves = []
    qrs_complexes = []
    t_waves = []

    out = ecg.ecg(signal=ecg_signal, sampling_rate=fs, show=False)
    rpeaks = out["rpeaks"]
    rr_intervals = np.diff(rpeaks)
    average_rr_interval = np.mean(rr_intervals)

    signal_len = len(ecg_signal)

    for r_peak in rpeaks:
        start, end = (
            max(int(r_peak - average_rr_interval * 0.3), 0),
            min(int(r_peak + average_rr_interval * 0.5), signal_len - 1),
        )

        heartbeat = ecg_signal[start:end]

        # Skip heartbeats below a certain length threshold
        if len(heartbeat) < average_rr_interval * 0.5:
            continue

        # Append the heartbeat and corresponding interval
        heartbeats.append(heartbeat)
        heartbeat_intervals.append((start, end))

        # Simple approach to extract P-waves, QRS complexes, and T-waves in the range of the heartbeat
        p_wave_end = start + int((end - start) * 0.2)
        qrs_complex_end = p_wave_end + int((end - start) * 0.4)

        p_wave = ecg_signal[start:p_wave_end]
        qrs_complex = ecg_signal[p_wave_end:qrs_complex_end]
        t_wave = ecg_signal[qrs_complex_end:end]

        p_waves.append(p_wave)
        qrs_complexes.append(qrs_complex)
        t_waves.append(t_wave)

    return heartbeats, heartbeat_intervals, p_waves, qrs_complexes, t_waves
