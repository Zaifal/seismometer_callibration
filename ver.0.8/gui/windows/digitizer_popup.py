# kalibrasi_app/gui/windows/digitizer_popup.py

import customtkinter as ctk
from tkinter import messagebox
import json
import os

DIGITIZER_CONFIG_PATH = "data/digitizer_config.json"

class DigitizerPopup(ctk.CTkToplevel):
    def __init__(self, master, on_save_callback=None):
        super().__init__(master)
        self.title("Add New Digitizer")
        self.geometry("400x320")
        self.on_save_callback = on_save_callback

        self.entries = {}

        fields = ["Name", "Serial Number", "Resolution", "Full Scale Voltage"]
        for field in fields:
            label = ctk.CTkLabel(self, text=field)
            label.pack(pady=(10, 0))
            entry = ctk.CTkEntry(self)
            entry.pack(pady=(0, 10), fill="x", padx=20)
            self.entries[field] = entry

        save_btn = ctk.CTkButton(self, text="Save", command=self.save_digitizer)
        save_btn.pack(pady=20)

    def save_digitizer(self):
        data = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"{key} tidak boleh kosong.")
                return
            data[key] = value

        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(DIGITIZER_CONFIG_PATH):
            digitizers = []
        else:
            with open(DIGITIZER_CONFIG_PATH, "r") as f:
                digitizers = json.load(f)

        digitizers.append(data)

        with open(DIGITIZER_CONFIG_PATH, "w") as f:
            json.dump(digitizers, f, indent=4)

        messagebox.showinfo("Sukses", "Digitizer berhasil disimpan.")
        if self.on_save_callback:
            self.on_save_callback(data)  # Untuk memperbarui dropdown utama
        self.destroy()
