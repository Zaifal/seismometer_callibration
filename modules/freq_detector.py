import numpy as np
from obspy import Trace

def detect_amplitude_boundaries(trace: Trace, threshold_ratio=2.0, min_gap=0.5):
    """
    Mendeteksi batas frekuensi berdasarkan perubahan amplitudo signifikan.
    :param trace: Obspy Trace object
    :param threshold_ratio: Rasio perubahan amplitudo yang dianggap signifikan
    :param min_gap: Minimum waktu antar boundary (dalam detik)
    :return: List of waktu (detik) sebagai boundaries
    """
    data = trace.data
    fs = trace.stats.sampling_rate
    npts = len(data)

    peaks = []
    peak_times = []

    # Deteksi puncak dan lembah
    for i in range(1, npts - 1):
        if (data[i] > data[i - 1] and data[i] > data[i + 1]) or \
           (data[i] < data[i - 1] and data[i] < data[i + 1]):
            peaks.append(abs(data[i]))
            peak_times.append(i / fs)

    flat_boundaries = []
    last_amp = peaks[0]
    last_time = peak_times[0]

    for amp, t in zip(peaks[1:], peak_times[1:]):
        if amp == 0:
            continue
        ratio = amp / last_amp if last_amp != 0 else np.inf
        if ratio > threshold_ratio or ratio < 1 / threshold_ratio:
            if t - last_time > min_gap:
                flat_boundaries.append(t)
                last_time = t
                last_amp = amp
        else:
            last_amp = amp

    # Return sebagai list waktu tunggal (flat), bukan pasangan
    return flat_boundaries
