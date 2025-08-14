# kalibrasi_app/gui/windows/freq_selector_frame.py

import customtkinter as ctk

FREQUENCIES = [
    0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 20
]

class FreqSelectorFrame(ctk.CTkFrame):
    def __init__(self, parent, on_add_click):
        super().__init__(parent)
        self.on_add_click = on_add_click
        self.freq_widgets = {}

        title = ctk.CTkLabel(self, text="Asosiasi Frekuensi & Klik", font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

        for i, freq in enumerate(FREQUENCIES):
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(self, text=f"{freq} Hz", variable=var, command=lambda f=freq: self.toggle_freq(f))
            checkbox.grid(row=i+1, column=0, padx=(5, 2), pady=4, sticky="w")

            add_button = ctk.CTkButton(self, text="+ Tambah", width=80, height=28, command=lambda f=freq: self.add_letter(f))
            add_button.grid(row=i+1, column=1, padx=2, pady=4, sticky="w")

            label_frame = ctk.CTkFrame(self, height=32, fg_color="transparent")
            label_frame.grid(row=i+1, column=2, padx=(5, 5), pady=4, sticky="ew")
            label_frame.grid_propagate(False)

            self.freq_widgets[freq] = {
                "enabled": var,
                "label_frame": label_frame,
                "add_button": add_button,
                "labels": []
            }
            self.toggle_freq(freq)

    def toggle_freq(self, freq):
        state = "normal" if self.freq_widgets[freq]["enabled"].get() else "disabled"
        self.freq_widgets[freq]["add_button"].configure(state=state)

    def add_letter(self, freq):
        if callable(self.on_add_click):
            self.on_add_click(freq)

    def display_letters_for_freq(self, freq, letters):
        for lbl in self.freq_widgets[freq]["labels"]:
            lbl.destroy()
        self.freq_widgets[freq]["labels"].clear()
        
        for letter in letters:
            lbl = ctk.CTkLabel(
                self.freq_widgets[freq]["label_frame"],
                text=letter, fg_color="gray30", corner_radius=5,
                height=24, width=24, anchor="center"
            )
            lbl.pack(side="left", padx=2, pady=2)
            self.freq_widgets[freq]["labels"].append(lbl)

    def remove_letter(self, letter):
        for freq, data in self.freq_widgets.items():
            labels_to_remove = [lbl for lbl in data["labels"] if lbl.cget("text") == letter]
            for lbl in labels_to_remove:
                lbl.destroy()
                data["labels"].remove(lbl)

    # BARU: Fungsi untuk mendapatkan status semua checkbox
    def get_all_freq_states(self):
        """
        Mengembalikan dictionary berisi status semua frekuensi.
        Contoh: {0.01: True, 0.02: True, 0.05: False, ...}
        """
        states = {}
        for freq, widget_data in self.freq_widgets.items():
            states[freq] = widget_data["enabled"].get()
        return states