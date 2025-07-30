# kalibrasi_app/gui/plotting/plot_frame.py

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from obspy import Stream


class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, on_new_letter_callback=None, on_letter_removed_callback=None, on_clear_all_callback=None):
        super().__init__(parent)
        self.parent = parent
        
        # Inisialisasi semua variabel widget
        self.canvas = None
        self.toolbar = None
        self.amplitude_table = None
        self.bottom_frame = None # DIUBAH: Lacak frame toolbar
        
        self.letter_clicks = []
        self.letter_counter = 0
        self.current_ax = None
        self.fig = None
        
        self.on_new_letter_callback = on_new_letter_callback
        self.on_letter_removed_callback = on_letter_removed_callback
        self.on_clear_all_callback = on_clear_all_callback

    def clear_plot(self):
        """Membersihkan semua elemen plot, toolbar, dan tabel amplitudo secara tuntas."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # DIUBAH: Hancurkan bottom_frame yang berisi toolbar
        if self.bottom_frame:
            self.bottom_frame.destroy()

        if self.amplitude_table:
            self.amplitude_table.pack_forget()
            self.amplitude_table.destroy()

        # Reset semua referensi widget ke None
        self.canvas = None
        self.toolbar = None
        self.amplitude_table = None
        self.bottom_frame = None # DIUBAH
        
        # Reset variabel data plot
        self.letter_clicks.clear()
        self.letter_counter = 0
        self.current_ax = None
        self.fig = None

    def plot_stream(self, stream: Stream, channel_keys: list):
        self.clear_plot()
        num_channels = len(channel_keys)
        if num_channels == 0:
            return

        self.fig, axs = plt.subplots(nrows=num_channels, ncols=1, figsize=(10, 2 * num_channels), sharex=True, facecolor="#2b2b2b")
        if num_channels == 1:
            axs = [axs]

        for i, key in enumerate(channel_keys):
            try:
                station, location, channel = key.split(".")
                tr = stream.select(station=station, location=location, channel=channel).merge(method=1)[0]
                times = np.arange(len(tr.data)) / tr.stats.sampling_rate
                axs[i].plot(times, tr.data, label=key, color='cyan')
                axs[i].set_ylabel(key, rotation=0, labelpad=40, ha='right', color='white')
                axs[i].legend(loc="upper right")
                axs[i].tick_params(axis='y', colors='white')
                axs[i].set_facecolor("#212121")
            except Exception:
                axs[i].text(0.5, 0.5, f"Gagal memuat: {key}", ha='center', va='center', color='white')
        
        axs[-1].set_xlabel("Waktu (detik)", color='white')
        axs[-1].tick_params(axis='x', colors='white')
        self.fig.tight_layout()
        self._embed_plot()

    def plot_trace_with_boundaries(self, trace, boundaries: list):
        self.clear_plot()
        self.fig, ax = plt.subplots(figsize=(15, 4), facecolor="#2b2b2b")
        self.current_ax = ax
        times = np.arange(len(trace.data)) / trace.stats.sampling_rate
        ax.plot(times, trace.data, color='cyan', label=trace.id)
        for t in boundaries:
            ax.axvline(x=t, color='red', linewidth=1.5, linestyle='-')
        ax.set_title("Plot Sinyal & Batas Frekuensi (Klik untuk Menandai)", color='white')
        ax.set_xlabel("Waktu (detik)", color='white')
        ax.set_ylabel("Amplitudo", color='white')
        ax.legend()
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor("#212121")
        self.fig.tight_layout()
        self._embed_plot()
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

    def _embed_plot(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        
        # DIUBAH: Gunakan self.bottom_frame agar bisa diakses dari fungsi lain
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=5)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.bottom_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="left", fill="x", expand=True)
        
        # Panggil fungsi untuk membuat tombol interaksi
        self._create_interaction_buttons()

    def _create_interaction_buttons(self):
        # Tombol sekarang dibuat di dalam self.bottom_frame
        self.clear_button = ctk.CTkButton(self.bottom_frame, text="Clear Huruf", width=120, command=self.clear_all_letters)
        self.clear_button.pack(side="right", padx=5)
        self.undo_button = ctk.CTkButton(self.bottom_frame, text="Undo Huruf", width=120, command=self.undo_last_letter)
        self.undo_button.pack(side="right", padx=5)
        
    def on_click(self, event):
        if event.inaxes != self.current_ax or self.toolbar.mode:
            return
        time_clicked = event.xdata
        if time_clicked is None:
            return
        label = chr(65 + self.letter_counter)
        self.letter_counter += 1
        line = self.current_ax.axvline(x=time_clicked, color='orange', linestyle='--')
        text = self.current_ax.text(time_clicked, self.current_ax.get_ylim()[1] * 0.9, label,
                                    ha='center', va='bottom', fontsize=12, fontweight='bold', color='orange')
        self.letter_clicks.append({'label': label, 'time': time_clicked, 'line': line, 'text': text})
        self.canvas.draw()
        if self.on_new_letter_callback:
            self.on_new_letter_callback(label, time_clicked)

    def undo_last_letter(self):
        if not self.letter_clicks:
            return
        last_click = self.letter_clicks.pop()
        self.letter_counter -= 1
        last_click['line'].remove()
        last_click['text'].remove()
        self.canvas.draw()
        if self.on_letter_removed_callback:
            self.on_letter_removed_callback(last_click['label'])

    def clear_all_letters(self):
        if not self.letter_clicks:
            return
        for click in self.letter_clicks:
            click['line'].remove()
            click['text'].remove()
        self.letter_clicks.clear()
        self.letter_counter = 0
        self.canvas.draw()
        print("[INFO] Semua tanda klik pada plot telah dibersihkan.")
        if self.on_clear_all_callback:
            self.on_clear_all_callback()

    def show_amplitude_table(self, data_by_freq):
        if self.amplitude_table:
            self.amplitude_table.destroy()
            
        self.amplitude_table = ctk.CTkScrollableFrame(self, height=200)
        self.amplitude_table.pack(fill="x", padx=10, pady=5)
        headers = ["Freq (Hz)", "NS Max", "NS Min", "EW Max", "EW Min", "UD Max", "UD Min"]
        for col, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.amplitude_table, text=h, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=col, padx=5, pady=2, sticky="w")
        
        row_idx = 1
        for freq in sorted(data_by_freq.keys()):
            ch_data = data_by_freq[freq]
            ctk.CTkLabel(self.amplitude_table, text=str(freq), font=("Arial", 12, "bold")).grid(row=row_idx, column=0, padx=5, sticky="w")
            ns_pairs = ch_data.get("NS", [])
            ew_pairs = ch_data.get("EW", [])
            ud_pairs = ch_data.get("UD", [])
            max_rows = max(len(ns_pairs), len(ew_pairs), len(ud_pairs), 1)

            for i in range(max_rows):
                cr = row_idx + i
                if i < len(ns_pairs):
                    ctk.CTkLabel(self.amplitude_table, text=f"{ns_pairs[i][0]:.2f}").grid(row=cr, column=1, sticky="w")
                    ctk.CTkLabel(self.amplitude_table, text=f"{ns_pairs[i][1]:.2f}").grid(row=cr, column=2, sticky="w")
                if i < len(ew_pairs):
                    ctk.CTkLabel(self.amplitude_table, text=f"{ew_pairs[i][0]:.2f}").grid(row=cr, column=3, sticky="w")
                    ctk.CTkLabel(self.amplitude_table, text=f"{ew_pairs[i][1]:.2f}").grid(row=cr, column=4, sticky="w")
                if i < len(ud_pairs):
                    ctk.CTkLabel(self.amplitude_table, text=f"{ud_pairs[i][0]:.2f}").grid(row=cr, column=5, sticky="w")
                    ctk.CTkLabel(self.amplitude_table, text=f"{ud_pairs[i][1]:.2f}").grid(row=cr, column=6, sticky="w")
            row_idx += max_rows