# kalibrasi_app/gui/widgets/file_selector.py

from tkinter import filedialog
from obspy import read
from tkinter import messagebox

def load_seed_file(app_instance):
    """Membuka dialog file untuk memilih file SEED dan memuatnya ke aplikasi."""
    
    filepath = filedialog.askopenfilename(
        title="Pilih File SEED",
        filetypes=(("SEED files", "*.seed *.mseed"), ("All files", "*.*"))
    )
    
    if not filepath:
        return

    try:
        # Panggil fungsi reset di app_instance SEBELUM memuat data baru
        app_instance.reset_ui_to_initial_state()

        # Muat stream
        stream = read(filepath)
        
        # Gabungkan trace yang terpisah jika ada (penting untuk data yang terpotong)
        stream.merge(method=1)
        
        # Simpan stream ke instance aplikasi utama
        app_instance.stream = stream
        
        print(f"File berhasil dimuat: {filepath}")
        print("Stream Info:")
        print(app_instance.stream.__str__(extended=True))

        # Panggil fungsi untuk memperbarui plot dan menampilkan menu selanjutnya
        app_instance.update_plot_selected_channels()

    except Exception as e:
        messagebox.showerror("Error", f"Gagal memuat file SEED:\n{e}")
        app_instance.stream = None