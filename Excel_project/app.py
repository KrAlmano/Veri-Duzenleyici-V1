import customtkinter as ctk
from mixins.ui_parts import UiPartsMixin
from mixins.file_management import FileManagementMixin
from mixins.filtering import FilteringMixin
from mixins.data_export import DataExportMixin
from mixins.data_editor import DataEditorMixin

class VeriDuzenleyici(ctk.CTk, UiPartsMixin, FileManagementMixin, FilteringMixin, DataExportMixin, DataEditorMixin):
    def __init__(self):
        super().__init__()
        
        # CustomTkinter tema ayarları
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("Veri Düzenleyici V1")
        self.geometry("990x600+200+60")

        
        
        self.df = None
        self.df_filtered = None
        self.secili_dosya = None
        self.secili_klasor = None
        self.filtreler = []

        # Sağ tık menüsü için tkinter kullanıyoruz çünkü CustomTkinter'da CTkMenu yok
        import tkinter as tk
        self.sag_menu = tk.Menu(self, tearoff=0)
        self.sag_menu.add_command(label="Sil", command=self._dosya_sil)
        self.sag_menu.add_command(label="Yeniden Adlandır", command=self._dosya_yeniden_adlandir)

        self._style_treeviews()  # Tema stillerini uygula
        self._arayuz_olustur()
        self._dosya_agacini_guncelle()