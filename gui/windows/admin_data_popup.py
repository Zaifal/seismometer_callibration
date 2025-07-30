# kalibrasi_app/gui/windows/admin_data_popup.py

import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime
from tkcalendar import Calendar
import tkinter as tk

class AdminDataPopup(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback=None):
        super().__init__(master)
        self.title("Administration Data")
        self.geometry("400x600")
        self.entries = {}
        self.on_save_callback = on_save_callback

        self.fields = [
            "No Order/Identifikasi", "Nama Alat", "Merk", "Serial Number",
            "Tanggal Kalibrasi", "Suhu Ruang (°C)", "Kelembapan (%RH)",
            "konstanta koil"
        ]

        for field in self.fields:
            label = ctk.CTkLabel(self, text=field)
            label.pack(pady=(10, 0))

            if field == "Tanggal Kalibrasi":
                frame = tk.Frame(self)
                frame.pack(pady=(0, 10), padx=20, fill="x")
                self.calendar = Calendar(frame, selectmode='day', date_pattern='yyyy-mm-dd')
                self.calendar.pack(fill="x")
                self.entries[field] = self.calendar
            else:
                entry = ctk.CTkEntry(self)
                entry.pack(pady=(0, 10), fill="x", padx=20)
                self.entries[field] = entry

        save_btn = ctk.CTkButton(self, text="Save", command=self.save_data)
        save_btn.pack(pady=20)

    def save_data(self):
        data = {}
        for key, entry in self.entries.items():
            if key == "Tanggal Kalibrasi":
                value = entry.get_date()
            else:
                value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"{key} tidak boleh kosong.")
                return
            data[key] = value

        nama = data["Nama Alat"].replace(" ", "")
        sn = data["Serial Number"].replace(" ","-")
        tanggal = datetime.now().strftime("%Y-%m-%d")
        filename = f"{tanggal}_{nama}_{sn}.json"
        os.makedirs("data/admin_data", exist_ok=True)
        with open(f"data/admin_data/{filename}", "w") as f:
            json.dump(data, f, indent=4)

        if self.on_save_callback:
            self.on_save_callback(data)

        messagebox.showinfo("Sukses", "Data berhasil disimpan!")
        self.destroy()