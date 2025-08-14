# kalibrasi_app/modules/amplitude_extractor.py

import numpy as np
from scipy.signal import find_peaks

def find_best_amplitude_pairs(data_segment: np.ndarray, max_pairs=5):
    """
    Menerima segmen data dan menemukan pasangan amplitudo max-min terbaik.
    DIUBAH: Menambahkan syarat filter amplitudo minimum.
    """
    # Anda bisa mengubah nilai threshold di sini
    MINIMUM_AMPLITUDE_THRESHOLD = 30000

    if len(data_segment) < 20:
        return []

    # 1. Deteksi Indeks Puncak dan Lembah dengan prominence
    try:
        prominence_threshold = np.std(data_segment) * 0.2
        peak_indices, _ = find_peaks(data_segment, prominence=prominence_threshold)
        trough_indices, _ = find_peaks(-data_segment, prominence=prominence_threshold)
    except Exception:
        return []

    if len(peak_indices) == 0 or len(trough_indices) == 0:
        return []

    # 2. Gabungkan dan Tandai (Tagging)
    peaks = [{'index': i, 'value': data_segment[i], 'type': 'peak'} for i in peak_indices]
    troughs = [{'index': i, 'value': data_segment[i], 'type': 'trough'} for i in trough_indices]
    
    all_extrema = sorted(peaks + troughs, key=lambda x: x['index'])

    # 3. Pemasangan Berdasarkan Tipe
    pairs_with_indices = []
    for i in range(len(all_extrema) - 1):
        current_extrema = all_extrema[i]
        next_extrema = all_extrema[i+1]

        if current_extrema['type'] != next_extrema['type']:
            if current_extrema['type'] == 'peak':
                peak = current_extrema
                trough = next_extrema
            else:
                peak = next_extrema
                trough = current_extrema
            
            if peak['value'] > trough['value']:
                pairs_with_indices.append({'peak': peak, 'trough': trough})

    if not pairs_with_indices:
        return []

    # BARU: Langkah 4 - Filter berdasarkan ambang batas amplitudo minimum
    filtered_pairs = [
        p for p in pairs_with_indices
        if (p['peak']['value'] - p['trough']['value']) >= MINIMUM_AMPLITUDE_THRESHOLD
    ]

    # Jika tidak ada pasangan yang lolos filter, kembalikan list kosong
    if not filtered_pairs:
        print(f"[DEBUG] Tidak ada pasangan yang lolos threshold amplitudo {MINIMUM_AMPLITUDE_THRESHOLD}")
        return []
    
    # Jika pasangan yang lolos sudah sedikit, langsung kembalikan
    if len(filtered_pairs) <= max_pairs:
        return filtered_pairs

    # 5. Pilih Pasangan Terbaik dari yang sudah difilter
    # Logika "paling seragam" sekarang hanya bekerja pada sinyal-sinyal kuat.
    amplitudes = [p['peak']['value'] - p['trough']['value'] for p in filtered_pairs]
    mean_amplitude = np.mean(amplitudes)
    
    filtered_pairs.sort(key=lambda p: abs((p['peak']['value'] - p['trough']['value']) - mean_amplitude))
    
    return filtered_pairs[:max_pairs]