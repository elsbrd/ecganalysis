import numpy as np
import scipy


def to_letter(cluster_num):
    return chr(19968 + cluster_num)


def convert_labels_to_letters(labels):
    return [to_letter(label) for label in labels]


def concatenate_letters(letters_p, letters_qrs, letters_t):
    return [p + qrs + t for p, qrs, t in zip(letters_p, letters_qrs, letters_t)]


def extract_wave_features(p_waves, qrs_complexes, t_waves):
    p_wave_features = []
    qrs_complex_features = []
    t_wave_features = []
    print("sadfsdf")
    for p_wave, qrs_complex, t_wave in zip(p_waves, qrs_complexes, t_waves):
        # Compute features for P-wave
        p_wave_feature = _compute_features(p_wave)
        p_wave_features.append(p_wave_feature)

        # Compute features for QRS complex
        qrs_complex_feature = _compute_features(qrs_complex)
        qrs_complex_features.append(qrs_complex_feature)

        # Compute features for T-wave
        t_wave_feature = _compute_features(t_wave)
        t_wave_features.append(t_wave_feature)
    print("12234234")
    return p_wave_features, qrs_complex_features, t_wave_features


def word_to_vec(word, word2vec):
    return np.mean([word2vec.wv[letter] for letter in word], axis=0)


def _compute_features(wave):
    # Time-domain features
    mean = np.mean(wave)
    median = np.median(wave)
    std = np.std(wave)
    max_val = np.max(wave)
    min_val = np.min(wave)
    skewness = scipy.stats.skew(wave)

    # Calculate the FFT (Fast Fourier Transform) for frequency analysis
    fft = np.fft.fft(wave)

    # Calculate absolute value of fft to get power spectrum
    power = np.abs(fft)

    # Normalize power
    power_normalized = power / np.sum(power)

    # Calculate power spectral density
    psd = np.abs(fft) ** 2

    # Frequency-domain features
    spectral_entropy = -np.sum(
        power_normalized * np.log2(power_normalized + np.finfo(float).eps)
    )
    spectral_centroid = np.sum(np.arange(1, len(psd) + 1) * psd) / np.sum(psd)
    fundamental_freq = np.argmax(power)

    # Waveform characteristics
    wave_duration = len(wave)
    wave_amplitude = np.max(wave) - np.min(wave)

    return [
        mean,
        median,
        std,
        max_val,
        min_val,
        skewness,
        spectral_entropy,
        spectral_centroid,
        fundamental_freq,
        wave_duration,
        wave_amplitude,
    ]
