# kalibrasi_app/modules/amplitude_extractor.py

import numpy as np
from scipy.signal import find_peaks

def find_best_amplitude_pairs(data_segment: np.ndarray, max_pairs=5):
    """
    Menerima segmen data dan menemukan pasangan amplitudo max-min terbaik.
    DIUBAH: Logika pemasangan sekarang memastikan setiap puncak/lembah hanya
    digunakan dalam satu pasangan unik.
    """
    MINIMUM_AMPLITUDE_THRESHOLD = 30000

    if len(data_segment) < 20:
        return []

    # 1. Deteksi Indeks Puncak dan Lembah
    try:
        prominence_threshold = np.std(data_segment) * 0.2
        peak_indices, _ = find_peaks(data_segment, prominence=prominence_threshold)
        trough_indices, _ = find_peaks(-data_segment, prominence=prominence_threshold)
    except Exception:
        return []

    if len(peak_indices) == 0 or len(trough_indices) == 0:
        return []

    # 2. Siapkan Daftar Kandidat
    # Buat daftar dictionary untuk setiap puncak dan lembah
    peaks = [{'index': i, 'value': data_segment[i], 'used': False} for i in peak_indices]
    troughs = [{'index': i, 'value': data_segment[i], 'used': False} for i in trough_indices]
    
    # 3. Logika Pemasangan Unik
    pairs_with_indices = []
    
    # Iterasi melalui setiap puncak untuk mencari pasangan lembahnya
    for peak in peaks:
        if peak['used']: continue # Lewati jika puncak ini sudah dipasangkan

        # Cari lembah terdekat yang valid (setelah puncak dan belum digunakan)
        closest_trough = None
        min_distance = float('inf')

        for trough in troughs:
            if trough['used']: continue # Lewati lembah yang sudah dipasangkan
            
            # Cek apakah lembah berada setelah puncak
            if trough['index'] > peak['index']:
                distance = trough['index'] - peak['index']
                if distance < min_distance:
                    min_distance = distance
                    closest_trough = trough
        
        # Jika pasangan ditemukan
        if closest_trough:
            # Pastikan nilai puncak memang lebih besar dari lembah
            if peak['value'] > closest_trough['value']:
                pairs_with_indices.append({'peak': peak, 'trough': closest_trough})
                # Tandai keduanya sebagai sudah digunakan
                peak['used'] = True
                closest_trough['used'] = True

    if not pairs_with_indices:
        return []

    # 4. Filter berdasarkan ambang batas amplitudo minimum
    filtered_pairs = [
        p for p in pairs_with_indices
        if (p['peak']['value'] - p['trough']['value']) >= MINIMUM_AMPLITUDE_THRESHOLD
    ]

    if not filtered_pairs:
        return []
    
    if len(filtered_pairs) <= max_pairs:
        return filtered_pairs

    # 5. Pilih 5 Pasangan Terbaik dari yang sudah difilter
    amplitudes = [p['peak']['value'] - p['trough']['value'] for p in filtered_pairs]
    mean_amplitude = np.mean(amplitudes)
    
    filtered_pairs.sort(key=lambda p: abs((p['peak']['value'] - p['trough']['value']) - mean_amplitude))
    
    return filtered_pairs[:max_pairs]
