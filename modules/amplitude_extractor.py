# kalibrasi_app/modules/amplitude_extractor.py

import numpy as np
from scipy.signal import find_peaks

def find_best_amplitude_pairs(data_segment: np.ndarray, max_pairs=5):
    """
    Menerima sebuah segmen data dan menemukan pasangan amplitudo max-min terbaik.
    Fungsi ini mencari puncak dan lembah, memasangkannya, dan memilih
    pasangan yang paling seragam.

    :param data_segment: Array numpy dari data sinyal.
    :param max_pairs: Jumlah maksimal pasangan yang akan dikembalikan.
    :return: List berisi tuple pasangan amplitudo, contoh: [(max1, min1), (max2, min2), ...]
    """
    # Pastikan data cukup panjang untuk dianalisis
    if len(data_segment) < 20:
        return []

    # Temukan indeks puncak (maksimum) dan lembah (minimum)
    # prominence adalah ukuran seberapa "menonjol" sebuah puncak dari lingkungan sekitarnya.
    # Menggunakan standar deviasi untuk prominence membantu membuatnya adaptif terhadap noise sinyal.
    try:
        prominence_threshold = np.std(data_segment) * 0.2
        max_peaks_indices, _ = find_peaks(data_segment, prominence=prominence_threshold)
        min_peaks_indices, _ = find_peaks(-data_segment, prominence=prominence_threshold)
    except Exception:
        return [] # Gagal mendeteksi puncak

    # Dapatkan nilai amplitudo dari indeks yang ditemukan
    max_vals = [{'index': i, 'value': data_segment[i]} for i in max_peaks_indices]
    min_vals = [{'index': i, 'value': data_segment[i]} for i in min_peaks_indices]

    # Gabungkan semua titik ekstrem (puncak dan lembah) dan urutkan berdasarkan posisinya
    all_extrema = sorted(max_vals + min_vals, key=lambda x: x['index'])

    if not all_extrema:
        return []

    # Logika untuk memasangkan puncak (positif) dengan lembah (negatif) yang berdekatan
    pairs = []
    i = 0
    while i < len(all_extrema) - 1:
        current_extrema = all_extrema[i]
        next_extrema = all_extrema[i+1]
        
        # Skenario 1: Puncak diikuti oleh Lembah
        if current_extrema['value'] > 0 and next_extrema['value'] < 0:
            pairs.append((current_extrema['value'], next_extrema['value']))
            i += 2  # Lompat 2 karena sudah menemukan satu pasangan valid
        # Skenario 2: Lembah diikuti oleh Puncak (kita tetap simpan max, min)
        elif current_extrema['value'] < 0 and next_extrema['value'] > 0:
            pairs.append((next_extrema['value'], current_extrema['value']))
            i += 2
        else:
            i += 1  # Bukan pasangan valid (misal: puncak ke puncak), lanjut ke berikutnya

    if not pairs:
        return []
        
    # Pilih pasangan terbaik: urutkan berdasarkan selisih absolut terkecil.
    # Pasangan dengan selisih kecil cenderung berasal dari gelombang yang lebih seragam.
    pairs.sort(key=lambda p: abs(p[0] - abs(p[1])))
    
    # Kembalikan sejumlah `max_pairs` pasangan terbaik
    return pairs[:max_pairs]