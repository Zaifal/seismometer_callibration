# kalibrasi_app/gui/widgets/digitizer_selector.py

import customtkinter as ctk
import json
from ..windows.digitizer_popup import DigitizerPopup

class DigitizerSelector(ctk.CTkFrame):
    def __init__(self, parent, command=None):
        super().__init__(parent)
        self.command = command
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="Digitizer")
        self.label.pack(pady=(5,0))
        
        self.dropdown = ctk.CTkOptionMenu(
            self, 
            values=["Loading..."], 
            command=self.on_dropdown_select
        ) 
        self.dropdown.pack(pady=(0,10), padx=5, fill="x")
        
        self.load_digitizers()

    def on_dropdown_select(self, choice):
        if choice == "Add New...":
            popup = DigitizerPopup(self, on_save_callback=self.handle_new_digitizer)
            popup.grab_set()
        elif self.command:
            self.command(choice)

    def load_digitizers(self):
        try:
            with open("data/digitizer_config.json", "r") as f:
                digitizers = json.load(f)
                names = [d.get("Name", "N/A") for d in digitizers]
        except (FileNotFoundError, json.JSONDecodeError):
            names = []
        
        names.append("Add New...")
        self.dropdown.configure(values=names)
        
        if len(names) > 1:
            initial_choice = names[0]
            self.dropdown.set(initial_choice)
            self.on_dropdown_select(initial_choice)
        else:
            self.dropdown.set("Add New...")
    
    def handle_new_digitizer(self, new_data):
        print("Digitizer baru ditambahkan, me-reload daftar...")
        self.load_digitizers()
        new_name = new_data.get("Name")
        if new_name:
            self.dropdown.set(new_name)
            self.on_dropdown_select(new_name)