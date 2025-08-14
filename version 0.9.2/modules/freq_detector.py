# kalibrasi_app/modules/freq_detector.py

import numpy as np
from obspy import Trace
from scipy.signal import spectrogram
from scipy.fft import rfft, rfftfreq

def detect_frequency_boundaries(trace: Trace, min_gap_seconds=5.0):
    """
    Mendeteksi batas-batas sinyal berdasarkan perubahan frekuensi dominan
    menggunakan analisis spektogram.
    """
    fs = trace.stats.sampling_rate
    data = trace.data

    if len(data) < fs * 10:
        print("[WARNING] Sinyal terlalu pendek untuk analisis spektogram.")
        return []

    # 1. Hitung Spektogram
    f, t, Sxx = spectrogram(data, fs=fs, nperseg=int(fs*2), noverlap=int(fs*1.5))

    # 2. Cari Frekuensi Dominan di Setiap Waktu
    dominant_freq_indices = np.argmax(Sxx, axis=0)
    dominant_freqs_over_time = f[dominant_freq_indices]

    # 3. Deteksi Perubahan Drastis pada Frekuensi Dominan
    boundaries = []
    last_boundary_time = 0
    
    freq_diffs = np.abs(np.diff(dominant_freqs_over_time))
    
    # Ambang batas perubahan frekuensi yang dianggap signifikan
    change_thresholds = np.maximum(dominant_freqs_over_time[:-1] * 0.5, 0.1)

    for i in range(len(freq_diffs)):
        current_time = t[i]
        
        if freq_diffs[i] > change_thresholds[i] and (current_time - last_boundary_time) > min_gap_seconds:
            boundaries.append(current_time)
            last_boundary_time = current_time
            
    return boundaries

def detect_dominant_frequency(segment_data, sampling_rate):
    """
    Menganalisis segmen sinyal dan mengembalikan frekuensi dominannya menggunakan FFT.
    """
    N = len(segment_data)
    if N == 0:
        return 0

    # Lakukan FFT. rfft digunakan untuk sinyal riil (bukan kompleks) agar lebih efisien.
    yf = rfft(segment_data)
    xf = rfftfreq(N, 1 / sampling_rate)

    # Cari indeks dari puncak tertinggi di spektrum frekuensi
    # Kita abaikan komponen DC (frekuensi 0 Hz) dengan memulai dari indeks 1
    idx_peak = np.argmax(np.abs(yf[1:])) + 1
    
    # Dapatkan frekuensi yang sesuai dengan puncak tersebut
    dominant_frequency = xf[idx_peak]
    
    return dominant_frequency