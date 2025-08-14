import customtkinter as ctk
import pandas as pd
import sys
import tkinter as tk
from tkinter import ttk

class UiPartsMixin:
    """
    Uygulamanın arayüz bileşenlerini ve stillerini yöneten mixin sınıfı.
    """
    def _arayuz_olustur(self):
        """Ana arayüz çerçevelerini ve widget'larını oluşturur."""
        ana_frame = ctk.CTkFrame(self)
        ana_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sol panel: Dosya/klasör ağacı
        sol_frame = ctk.CTkFrame(ana_frame, width=250) 
        sol_frame.pack(side="left", fill="y", padx=(0, 10))
        sol_frame.pack_propagate(False) 
        
        ctk.CTkLabel(sol_frame, text="Veritabanı", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        tree_frame = ctk.CTkFrame(sol_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.dosya_tree = ttk.Treeview(tree_frame, show="tree")
        self.dosya_tree.pack(fill="both", expand=True)
        self.dosya_tree.bind('<<TreeviewSelect>>', self._dosya_agacinda_secildi)
        
        if sys.platform == 'darwin': #MacOS için 
            self.dosya_tree.bind('<Button-2>', self._treeview_sag_tik_menu)
            self.dosya_tree.bind('<Control-Button-1>', self._treeview_sag_tik_menu)
        self.dosya_tree.bind('<Button-3>', self._treeview_sag_tik_menu)
        
        ctk.CTkButton(sol_frame, text="Dosya Yükle", command=self.dosya_yukle).pack(pady=10, padx=10, fill="x")

        # Orta panel: Filtre ve tablo
        orta_frame = ctk.CTkFrame(ana_frame)
        orta_frame.pack(side="left", fill="both", expand=True)
        
        self._olustur_filtre_paneli(orta_frame)
        
        self.tablo_frame = ctk.CTkFrame(orta_frame)
        self.tablo_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(self.tablo_frame, show="headings")
        
        # Stil uygulanmış kaydırma çubukları
        self.vsb = ttk.Scrollbar(self.tablo_frame, orient="vertical",
                                  command=self.tree.yview, style="Vertical.TScrollbar")
        
        self.hsb = ttk.Scrollbar(self.tablo_frame, orient="horizontal",
                                  command=self.tree.xview, style="Horizontal.TScrollbar")
        
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Grid layout ile tablo ve scrollbar'ları yerleştir
        self.tablo_frame.grid_rowconfigure(0, weight=1)
        self.tablo_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        
        # Yatay scrollbar için sağ alt köşe alanını ayır
        self.tablo_frame.grid_columnconfigure(1, weight=0, minsize=12)
        self.tablo_frame.grid_rowconfigure(1, weight=0, minsize=12)

    def _style_treeviews(self):
        """
        Uygulamadaki tüm standart ttk widget'larını koyu temaya uyumlu hale getirir.
        Bu metodun ana sınıfın __init__ fonksiyonunda çağrılması gerekir.
        """
        style = ttk.Style()
        style.theme_use("clam")

        BG_COLOR = "#1e1e1e"      # Ana arkaplan (çok koyu gri)
        FG_COLOR = "#e0e0e0"      # Metin rengi (açık gri)
        HEADER_BG = "#2d2d30"     # Başlık arkaplanı (koyu gri)
        SELECTED_BG = "#007acc"   # Seçili öğe arkaplanı (mavi)
        BORDER_COLOR = "#3e3e42"  # Kenarlık rengi

        # Treeview Stil Ayarları
        style.configure("Treeview",
                        background=BG_COLOR,
                        foreground=FG_COLOR,
                        fieldbackground=BG_COLOR,
                        font=("Calibri", 12),
                        rowheight=28,
                        borderwidth=1,
                        bordercolor=BORDER_COLOR)
        style.map('Treeview', background=[('selected', SELECTED_BG)])

        # Treeview Başlık Stil Ayarları
        style.configure("Treeview.Heading",
                        background=HEADER_BG,
                        foreground=FG_COLOR,
                        font=('Calibri', 12, 'bold'),
                        relief="flat",
                        borderwidth=1,
                        bordercolor=BORDER_COLOR)
        style.map("Treeview.Heading", background=[('active', '#3e3e42')])

        # Scrollbar Stil Ayarları
        style.configure("Vertical.TScrollbar", 
                        background=HEADER_BG, 
                        troughcolor=BG_COLOR, 
                        bordercolor=BORDER_COLOR, 
                        arrowcolor=FG_COLOR,
                        width=12)
        
        style.configure("Horizontal.TScrollbar", 
                        background=HEADER_BG, 
                        troughcolor=BG_COLOR, 
                        bordercolor=BORDER_COLOR, 
                        arrowcolor=FG_COLOR,
                        width=12)

    def _tabloyu_goster(self, df):
        """Verilen DataFrame'i ana veri tablosunda gösterir."""
        # Önceki verileri temizle
        self.tree.delete(*self.tree.get_children())
        
        if df is None:
            self.tree['columns'] = []
            return

        # Tarih sütunlarını düzgün formatla göster
        df_display = df.copy()
        for col in df_display.columns:
            if hasattr(self, '_kolon_tipi_bul') and self._kolon_tipi_bul(col) == 'tarih':
                try:    
                    # Önce NaN değerleri kontrol et
                    df_display[col] = df_display[col].astype(str)
                    # NaN string'lerini boş string yap
                    df_display[col] = df_display[col].replace(['nan', 'NaN', 'NaT'], '')
                    # Boş olmayan değerleri tarihe çevir
                    mask = df_display[col].str.strip() != ''
                    if mask.any():
                        # Farklı tarih formatlarını dene
                        temp_dates = pd.to_datetime(df_display[col][mask], errors='coerce')
                        # Başarılı parse edilenleri formatla
                        valid_dates = temp_dates.notna()
                        if valid_dates.any():
                            df_display.loc[mask & valid_dates, col] = temp_dates[valid_dates].dt.strftime('%d.%m.%Y')
                        # Başarısız olanları boş bırak
                        df_display.loc[mask & ~valid_dates, col] = ''
                except Exception:
                    pass
        
        self.tree['columns'] = list(df_display.columns)
        for col in df_display.columns:
            # Tarih sütunları için başlığa sıralama komutu ekleme
            if hasattr(self, '_kolon_tipi_bul') and self._kolon_tipi_bul(col) == 'tarih':
                self.tree.heading(col, text=col)
            else:
                self.tree.heading(col, text=col, command=lambda c=col: self._sutun_sirala(c))
            # Sabit genişlik ayarla - sütunlar yeniden boyutlandırılmasın
            self.tree.column(col, width=150, anchor="w", minwidth=100, stretch=False)
        
        for _, row in df_display.iterrows():
            self.tree.insert('', "end", values=list(row))
        
        # Yatay scrollbar'ın çalışması için sütunları ayarla
        self.update_idletasks()
        if not df_display.empty:
            for col in df_display.columns:
                # Her sütun için sabit genişlik kullan
                col_width = 150
                self.tree.column(col, width=col_width, minwidth=100, stretch=False)
