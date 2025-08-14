# kalibrasi_app/gui/plotting/plot_frame.py

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from obspy import Stream
import os

class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, on_boundaries_deleted_in_range=None):
        super().__init__(parent)
        self.parent = parent
        self.on_boundaries_deleted_in_range = on_boundaries_deleted_in_range
        
        # Inisialisasi semua variabel widget
        self.canvas = None
        self.toolbar = None
        self.amplitude_table = None
        self.bottom_frame = None
        
        self.current_ax = None
        self.fig = None
        self.plotted_points = []
        self.annotations = []
        self.boundary_lines = []

        # Variabel untuk drag-delete
        self.drag_start_x = None
        self.selection_rect = None

    def clear_plot(self):
        """Membersihkan semua elemen plot, toolbar, tabel, dan anotasi secara tuntas."""
        if self.canvas: self.canvas.get_tk_widget().destroy()
        if self.bottom_frame: self.bottom_frame.destroy()
        if self.amplitude_table: self.amplitude_table.pack_forget(); self.amplitude_table.destroy()

        self.clear_annotations()
        self.clear_points()
        self.clear_boundaries()
        
        # Reset semua referensi widget ke None
        self.canvas = self.toolbar = self.amplitude_table = self.bottom_frame = None
        self.current_ax = self.fig = None

    def clear_annotations(self):
        """Menghapus semua kotak warna dan teks anotasi dari plot."""
        for annotation in self.annotations:
            annotation.remove()
        self.annotations.clear()
        if self.canvas:
            self.canvas.draw()

    def clear_points(self):
        """Menghapus semua titik sampel biru dari plot."""
        for point in self.plotted_points:
            point.remove()
        self.plotted_points.clear()

    def clear_boundaries(self):
        """Menghapus semua garis boundary merah dari plot."""
        for line in self.boundary_lines:
            line.remove()
        self.boundary_lines.clear()

    def add_boundaries(self, boundaries):
        """Menambahkan garis boundary ke semua subplot yang ada."""
        if not self.fig or not self.fig.axes: return
        self.clear_boundaries()
        for ax in self.fig.axes:
            for t in boundaries:
                line = ax.axvline(x=t, color='red', linewidth=1.5, linestyle='-')
                self.boundary_lines.append(line)
        self.canvas.draw()
        
    def add_frequency_annotations(self, segments):
        """Menggambar kotak berwarna dan teks untuk setiap segmen frekuensi yang teridentifikasi."""
        if not self.fig or not self.fig.axes: return
        self.clear_annotations()
        colors = plt.cm.get_cmap('tab10', 10).colors
        main_ax = self.fig.axes[0] # Anotasi digambar relatif terhadap sumbu utama
        for i, (start_time, end_time, freq) in enumerate(segments):
            color = colors[i % len(colors)]
            span = main_ax.axvspan(start_time, end_time, color=color, alpha=0.3)
            text_x = start_time + (end_time - start_time) / 2
            text_y = main_ax.get_ylim()[1] * 0.9
            text = main_ax.text(text_x, text_y, f"{freq} Hz", 
                                        ha='center', va='top', color='white', 
                                        fontweight='bold', fontsize=10,
                                        bbox=dict(facecolor=color, alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'))
            self.annotations.append(span)
            self.annotations.append(text)
        self.canvas.draw()

    def plot_stream(self, stream: Stream, channel_keys: list):
        self.clear_plot()
        num_channels = len(channel_keys)
        if num_channels == 0: return

        self.fig, axs = plt.subplots(nrows=num_channels, ncols=1, figsize=(10, 2 * num_channels), sharex=True, facecolor="#2b2b2b")
        if num_channels == 1: axs = [axs]
        
        self.current_ax = axs[0]

        for i, key in enumerate(channel_keys):
            try:
                station, loc, ch = key.split(".")
                tr = stream.select(station=station, location=loc, channel=ch).merge(method=1)[0]
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

    def _embed_plot(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=5)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.bottom_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="left", fill="x", expand=True)
        
        # Hubungkan semua event mouse yang dibutuhkan
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event):
        """Dipanggil saat mouse diklik, memulai proses drag."""
        if not self.parent.delete_mode.get() or event.inaxes is None or self.toolbar.mode:
            return
        
        self.drag_start_x = event.xdata
        self.selection_rect = self.current_ax.axvspan(self.drag_start_x, self.drag_start_x, color='yellow', alpha=0.3)
        self.canvas.draw()

    def on_motion(self, event):
        """Dipanggil saat mouse digeser, mengupdate visual drag."""
        if self.drag_start_x is None or event.inaxes is None:
            return
        
        end_x = event.xdata
        if end_x is None: return
        
        self.selection_rect.set_xy([[self.drag_start_x, 0], [self.drag_start_x, 1], [end_x, 1], [end_x, 0], [self.drag_start_x, 0]])
        self.canvas.draw_idle()

    def on_release(self, event):
        """Dipanggil saat klik mouse dilepas, mengeksekusi hapus area."""
        if self.drag_start_x is None:
            return

        start_x = self.drag_start_x
        end_x = event.xdata
        
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

        if end_x is None:
            self.drag_start_x = None
            self.canvas.draw()
            return
            
        selection_min = min(start_x, end_x)
        selection_max = max(start_x, end_x)

        lines_to_delete = []
        times_to_delete = []
        
        for line in self.boundary_lines:
            line_time = line.get_xdata()[0]
            if selection_min <= line_time <= selection_max:
                lines_to_delete.append(line)
                times_to_delete.append(line_time)
        
        if lines_to_delete:
            for line in lines_to_delete:
                line.remove()
            
            if self.on_boundaries_deleted_in_range:
                self.on_boundaries_deleted_in_range(times_to_delete)
            
            print(f"{len(times_to_delete)} boundary dihapus.")

        self.canvas.draw()
        self.drag_start_x = None
            
    def plot_selected_points(self, points_to_plot):
        if not self.fig or not self.fig.axes: return
        self.clear_points()

        for ax in self.fig.axes:
            if not ax.get_legend(): continue
            legend_label = ax.get_legend().get_texts()[0].get_text()
            
            if legend_label in points_to_plot:
                points = points_to_plot[legend_label]
                times = [p[0] for p in points]
                values = [p[1] for p in points]
                
                plotted = ax.plot(times, values, 'bo', markersize=5, label='Amplitudo Terpilih', zorder=10)
                self.plotted_points.extend(plotted)

        handles, labels = self.fig.axes[-1].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.fig.axes[-1].legend(by_label.values(), by_label.keys(), loc='upper right')

        self.canvas.draw()
        print(f"[INFO] {len(self.plotted_points)} titik sampel ditampilkan.")

    def show_amplitude_table(self, data_by_freq):
        if self.amplitude_table: self.amplitude_table.destroy()
        self.amplitude_table = ctk.CTkScrollableFrame(self, height=200)
        self.amplitude_table.pack(fill="x", padx=10, pady=5)
        headers = ["Freq (Hz)", "NS Max", "NS Min", "EW Max", "EW Min", "UD Max", "UD Min"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.amplitude_table, text=h, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=5, pady=2, sticky="w")
        row_idx = 1
        for freq in sorted(data_by_freq.keys()):
            ch_data = data_by_freq[freq]
            ctk.CTkLabel(self.amplitude_table, text=str(freq), font=("Arial", 12, "bold")).grid(row=row_idx, column=0, padx=5, sticky="w")
            ns_pairs = ch_data.get("NS", []); ew_pairs = ch_data.get("EW", []); ud_pairs = ch_data.get("UD", [])
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
