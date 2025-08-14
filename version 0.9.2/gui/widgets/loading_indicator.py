# kalibrasi_app/gui/widgets/loading_indicator.py

import customtkinter as ctk

class LoadingIndicator(ctk.CTkToplevel):
    def __init__(self, master, title="Memproses..."):
        super().__init__(master)
        self.title("Loading")
        
        # Atur agar window tidak bisa diubah ukurannya dan tanpa title bar
        self.overrideredirect(True)
        self.geometry("200x100")
        
        # Posisikan di tengah window utama
        master_x = master.winfo_x()
        master_y = master.winfo_y()
        master_width = master.winfo_width()
        master_height = master.winfo_height()
        self.geometry(f"+{master_x + master_width // 2 - 100}+{master_y + master_height // 2 - 50}")

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.label = ctk.CTkLabel(self.frame, text=title, font=ctk.CTkFont(size=14))
        self.label.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.frame, mode='indeterminate')
        self.progress_bar.pack(pady=5, padx=10, fill="x", expand=True)
        self.progress_bar.start()

        self.lift() # Bawa ke depan
        self.grab_set() # Fokuskan window ini

    def stop(self):
        self.grab_release()
        self.destroy()