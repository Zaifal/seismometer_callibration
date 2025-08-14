# kalibrasi_app/gui/windows/admin_data_popup.py

import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime
from tkcalendar import Calendar
import tkinter as tk

class AdminDataPopup(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback=None, existing_data=None):
        super().__init__(master)
        self.title("Data Administrasi Sertifikat")
        self.geometry("500x700")
        self.on_save_callback = on_save_callback
        self.entries = {}

        # Buat sebuah frame utama yang bisa di-scroll
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_view = ctk.CTkTabview(main_frame, width=460)
        self.tab_view.pack(padx=5, pady=5, fill="both", expand=True)

        self.tab_view.add("Alat & Pemilik")
        self.tab_view.add("Data Kalibrasi")
        self.tab_view.add("Nomor Sertifikat")

        self._create_alat_pemilik_tab(self.tab_view.tab("Alat & Pemilik"))
        self._create_kalibrasi_tab(self.tab_view.tab("Data Kalibrasi"))
        self._create_sertifikat_tab(self.tab_view.tab("Nomor Sertifikat"))

        save_btn = ctk.CTkButton(main_frame, text="Save Data", command=self.save_data)
        save_btn.pack(pady=20, padx=10)

        if existing_data:
            self._populate_fields(existing_data)
        
        self.grab_set()

    def _create_entry(self, parent, field_name, row):
        label = ctk.CTkLabel(parent, text=field_name, anchor="w")
        label.grid(row=row, column=0, padx=10, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row+1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.entries[field_name] = entry
        return row + 2

    def _create_alat_pemilik_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        alat_label = ctk.CTkLabel(tab, text="Data Alat", font=ctk.CTkFont(size=14, weight="bold"))
        alat_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        row_idx = 1
        row_idx = self._create_entry(tab, "Nama Alat", row_idx)
        row_idx = self._create_entry(tab, "Merk", row_idx)
        row_idx = self._create_entry(tab, "Tipe", row_idx)
        row_idx = self._create_entry(tab, "No Seri", row_idx)
        pemilik_label = ctk.CTkLabel(tab, text="Data Pemilik", font=ctk.CTkFont(size=14, weight="bold"))
        pemilik_label.grid(row=row_idx, column=0, padx=10, pady=(20, 10), sticky="w")
        row_idx += 1
        row_idx = self._create_entry(tab, "Nama Pemilik", row_idx)
        row_idx = self._create_entry(tab, "Stasiun", row_idx)
        row_idx = self._create_entry(tab, "Kode", row_idx)
        row_idx = self._create_entry(tab, "Alamat", row_idx)
        
    def _create_kalibrasi_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        row_idx = 0
        for field in ["Tanggal Masuk", "Tanggal Kalibrasi", "Tanggal Laporan"]:
            label = ctk.CTkLabel(tab, text=field, anchor="w")
            label.grid(row=row_idx, column=0, padx=10, pady=(10, 0), sticky="w")
            calendar = Calendar(tab, selectmode='day', date_pattern='yyyy-mm-dd')
            calendar.grid(row=row_idx+1, column=0, padx=10, pady=(0, 10), sticky="ew")
            self.entries[field] = calendar
            row_idx += 2
        tempat_frame = ctk.CTkFrame(tab)
        tempat_frame.grid(row=row_idx, column=0, padx=10, pady=(10,0), sticky="ew")
        tempat_frame.grid_columnconfigure(0, weight=1)
        row_idx += 1
        ctk.CTkLabel(tempat_frame, text="Tempat Kalibrasi (Jalan)").pack(anchor="w", padx=5)
        self.entries["Tempat Kalibrasi (Jalan)"] = ctk.CTkEntry(tempat_frame)
        self.entries["Tempat Kalibrasi (Jalan)"].pack(fill="x", expand=True, padx=5)
        ctk.CTkLabel(tempat_frame, text="Tempat Kalibrasi (Kota-Provinsi)").pack(anchor="w", pady=(5,0), padx=5)
        self.entries["Tempat Kalibrasi (Kota-Provinsi)"] = ctk.CTkEntry(tempat_frame)
        self.entries["Tempat Kalibrasi (Kota-Provinsi)"].pack(fill="x", expand=True, pady=(0,5), padx=5)
        kondisi_frame = ctk.CTkFrame(tab)
        kondisi_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        kondisi_frame.grid_columnconfigure((0,1), weight=1)
        row_idx += 1
        ctk.CTkLabel(kondisi_frame, text="Suhu Awal (°C)").grid(row=0, column=0, padx=5, sticky="w")
        self.entries["Suhu Awal (°C)"] = ctk.CTkEntry(kondisi_frame, width=150)
        self.entries["Suhu Awal (°C)"].grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkLabel(kondisi_frame, text="Suhu Akhir (°C)").grid(row=0, column=1, padx=5, sticky="w")
        self.entries["Suhu Akhir (°C)"] = ctk.CTkEntry(kondisi_frame, width=150)
        self.entries["Suhu Akhir (°C)"].grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(kondisi_frame, text="Kelembaban Awal (%RH)").grid(row=2, column=0, padx=5, sticky="w")
        self.entries["Kelembaban Awal (%RH)"] = ctk.CTkEntry(kondisi_frame, width=150)
        self.entries["Kelembaban Awal (%RH)"].grid(row=3, column=0, padx=5, pady=5)
        ctk.CTkLabel(kondisi_frame, text="Kelembaban Akhir (%RH)").grid(row=2, column=1, padx=5, sticky="w")
        self.entries["Kelembaban Akhir (%RH)"] = ctk.CTkEntry(kondisi_frame, width=150)
        self.entries["Kelembaban Akhir (%RH)"].grid(row=3, column=1, padx=5, pady=5)

    def _create_sertifikat_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        row_idx = 0
        row_idx = self._create_entry(tab, "Nomor Identifikasi", row_idx)
        row_idx = self._create_entry(tab, "No Order", row_idx)
        row_idx = self._create_entry(tab, "TTD", row_idx)
        row_idx = self._create_entry(tab, "Bulan (Romawi)", row_idx)
        row_idx = self._create_entry(tab, "Tahun", row_idx)
        row_idx = self._create_entry(tab, "Diverifikasi Oleh", row_idx)
        row_idx = self._create_entry(tab, "Divalidasi Oleh", row_idx)
        disahkan_frame = ctk.CTkFrame(tab)
        disahkan_frame.grid(row=row_idx, column=0, padx=10, pady=10, sticky="ew")
        disahkan_frame.grid_columnconfigure(0, weight=1)
        row_idx += 1
        ctk.CTkLabel(disahkan_frame, text="Disahkan Oleh", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        ctk.CTkLabel(disahkan_frame, text="Pangkat").pack(anchor="w", padx=5, pady=(5,0))
        self.entries["Disahkan Oleh - Pangkat"] = ctk.CTkEntry(disahkan_frame)
        self.entries["Disahkan Oleh - Pangkat"].pack(fill="x", padx=5, pady=(0,5))
        ctk.CTkLabel(disahkan_frame, text="Nama").pack(anchor="w", padx=5, pady=(5,0))
        self.entries["Disahkan Oleh - Nama"] = ctk.CTkEntry(disahkan_frame)
        self.entries["Disahkan Oleh - Nama"].pack(fill="x", padx=5, pady=(0,5))
        ctk.CTkLabel(disahkan_frame, text="NIP").pack(anchor="w", padx=5, pady=(5,0))
        self.entries["Disahkan Oleh - NIP"] = ctk.CTkEntry(disahkan_frame)
        self.entries["Disahkan Oleh - NIP"].pack(fill="x", padx=5, pady=(0,5))

    def _populate_fields(self, data):
        for key, entry_widget in self.entries.items():
            if key in data:
                value = data[key]
                if isinstance(entry_widget, Calendar):
                    try:
                        entry_widget.set_date(value)
                    except:
                        print(f"Gagal mengatur tanggal untuk '{key}' dengan nilai '{value}'")
                elif isinstance(entry_widget, ctk.CTkEntry):
                    entry_widget.delete(0, 'end')
                    entry_widget.insert(0, value)
    
    def save_data(self):
        data = {}
        try:
            for key, widget in self.entries.items():
                if isinstance(widget, Calendar):
                    data[key] = widget.get_date()
                else: # ctk.CTkEntry
                    value_str = widget.get().strip()
                    
                    # DIUBAH: Konversi Suhu dan Kelembaban ke integer
                    if 'Suhu' in key or 'Kelembaban' in key:
                        if not value_str: # Boleh kosong atau harus diisi? Asumsi harus diisi.
                            messagebox.showerror("Error", f"Kolom '{key}' tidak boleh kosong.")
                            return
                        # Coba konversi ke integer
                        data[key] = int(value_str)
                    else:
                        # Untuk kolom lain, simpan sebagai string biasa
                        data[key] = value_str
        
        # Tangani error jika pengguna memasukkan teks bukan angka
        except ValueError:
            messagebox.showerror("Error", f"Input untuk kolom Suhu atau Kelembaban harus berupa angka bulat (integer).")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
            return

        # Validasi umum
        if not data.get("Nama Alat") or not data.get("No Seri"):
            messagebox.showerror("Error", "Nama Alat dan No Seri tidak boleh kosong.")
            return

        # Kirim data kembali ke jendela utama
        if self.on_save_callback:
            self.on_save_callback(data)
        
        # (Opsional) Simpan backup ke JSON
        nama_alat = data.get("Nama Alat", "unknown").replace(" ", "")
        sn = data.get("No Seri", "unknown").replace(" ","-")
        tanggal = datetime.now().strftime("%Y-%m-%d")
        filename = f"{tanggal}_{nama_alat}_{sn}.json"
        os.makedirs("data/admin_data", exist_ok=True)
        with open(os.path.join("data/admin_data", filename), "w") as f:
            # Konversi semua data ke string untuk kompatibilitas JSON
            json_data = {k: str(v) for k, v in data.items()}
            json.dump(json_data, f, indent=4)

        messagebox.showinfo("Sukses", "Data administrasi berhasil disimpan!")
        self.destroy()