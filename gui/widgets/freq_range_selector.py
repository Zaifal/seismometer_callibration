# kalibrasi_app/gui/widgets/freq_range_selector.py

import customtkinter as ctk

class FreqRangeSelector(ctk.CTkFrame):
    def __init__(self, parent, all_letters, on_add_range):
        super().__init__(parent)
        self.all_letters = all_letters
        self.on_add_range = on_add_range
        self.freq_rows = {}

        self.frequencies = [
            0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
            1, 2, 5, 10, 15, 20
        ]

        for freq in self.frequencies:
            row = ctk.CTkFrame(self)
            row.pack(fill="x", pady=2, padx=5)

            checkbox_var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(row, variable=checkbox_var, text="")
            checkbox.pack(side="left", padx=(0, 5))

            label = ctk.CTkLabel(row, text=f"{freq} Hz", width=60)
            label.pack(side="left")

            add_btn = ctk.CTkButton(row, text="+", width=30, command=lambda f=freq: self.add_range(f))
            add_btn.pack(side="left", padx=5)

            letter_frame = ctk.CTkFrame(row)
            letter_frame.pack(side="left", padx=5, fill="x", expand=True)

            self.freq_rows[freq] = {
                "checkbox_var": checkbox_var,
                "add_btn": add_btn,
                "letter_frame": letter_frame,
                "letters": [],
                "checkbox": checkbox
            }

            checkbox.configure(command=lambda f=freq: self.toggle_row(f))

    def toggle_row(self, freq):
        row = self.freq_rows[freq]
        if row["checkbox_var"].get():
            row["add_btn"].configure(state="normal", fg_color="#1f6aa5")
        else:
            row["add_btn"].configure(state="disabled", fg_color="gray")

    def add_range(self, freq):
        row = self.freq_rows[freq]
        letter = self.on_add_range(freq)
        if letter and letter not in row["letters"]:
            row["letters"].append(letter)
            lbl = ctk.CTkLabel(row["letter_frame"], text=letter)
            lbl.pack(side="left", padx=2)

    def get_selected_ranges(self):
        result = {}
        for freq, row in self.freq_rows.items():
            if row["checkbox_var"].get() and row["letters"]:
                result[freq] = row["letters"]
        return result

    def reset(self):
        for row in self.freq_rows.values():
            for widget in row["letter_frame"].winfo_children():
                widget.destroy()
            row["letters"] = []
            row["checkbox_var"].set(True)
            row["add_btn"].configure(state="normal", fg_color="#1f6aa5")
    
    def remove_letter(self, letter):
        for freq, row in self.freq_rows.items():
            if letter in row["letters"]:
                row["letters"].remove(letter)
                for widget in row["letter_frame"].winfo_children():
                    if widget.cget("text") == letter:
                        widget.destroy()
                        break

