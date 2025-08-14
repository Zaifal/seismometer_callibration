# kalibrasi_app/gui/windows/frequency_domain_popup.py

import customtkinter as ctk
import numpy as np
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FrequencyDomainPopup(ctk.CTkToplevel):
    def __init__(self, master, trace):
        super().__init__(master)
        self.title(f"Analisis Domain Frekuensi - {trace.id}")
        self.geometry("800x600")

        self.trace = trace

        # Frame utama untuk plot
        plot_frame = ctk.CTkFrame(self)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panggil fungsi untuk menghitung dan menggambar plot
        self._calculate_and_plot_fft(plot_frame)
        
        # Agar window ini menjadi fokus utama
        self.grab_set()

    def _calculate_and_plot_fft(self, parent_frame):
        data = self.trace.data
        fs = self.trace.stats.sampling_rate
        N = len(data)

        if N == 0:
            ctk.CTkLabel(parent_frame, text="Tidak ada data untuk dianalisis.").pack(pady=20)
            return

        # Hitung FFT. rfft digunakan untuk sinyal riil agar lebih efisien.
        yf = rfft(data)
        xf = rfftfreq(N, 1 / fs)

        # Buat plot menggunakan Matplotlib
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="#2b2b2b")
        ax.plot(xf, np.abs(yf), color="cyan")
        
        # Styling plot agar sesuai tema
        ax.set_title("Spektrum Domain Frekuensi", color="white")
        ax.set_xlabel("Frekuensi (Hz)", color="white")
        ax.set_ylabel("Amplitudo Spektral", color="white")
        ax.set_xscale('log')  # Skala logaritmik cocok untuk melihat spektrum frekuensi
        ax.set_yscale('log')
        ax.grid(True, which="both", ls="--", color="gray", alpha=0.5)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor("#212121")
        
        fig.tight_layout()

        # Masukkan plot Matplotlib ke dalam window CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)