# file: gui/widgets/channel_selector.py

import customtkinter as ctk

class ChannelSelector(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.selected_channels = [ctk.StringVar(), ctk.StringVar(), ctk.StringVar()]
        self.labels = ["East-West", "North-South", "Up-Down"]
        self.dropdowns = []

        for i in range(3):
            label = ctk.CTkLabel(self, text=self.labels[i])
            label.pack()
            dropdown = ctk.CTkOptionMenu(self, variable=self.selected_channels[i], values=[])
            dropdown.pack(pady=5)
            self.dropdowns.append(dropdown)

        self.hide()

    def set_channels(self, stream, available_keys):
        # Set values and reset selection
        for i in range(3):
            self.dropdowns[i].configure(values=available_keys)
            if len(available_keys) > i:
                self.selected_channels[i].set(available_keys[i])
            else:
                self.selected_channels[i].set("")

    def get_selected_channels(self):
        # Kembalikan channel pertama sebagai referensi untuk klasifikasi
        return self.selected_channels[0].get()

    def get_all_selected(self):
        # Kembalikan ketiga channel
        return [var.get() for var in self.selected_channels]

    def show(self):
        self.pack(pady=10)

    def hide(self):
        self.pack_forget()
