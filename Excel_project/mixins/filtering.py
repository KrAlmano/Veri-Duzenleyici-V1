import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import re

class FilteringMixin:
    def _olustur_filtre_paneli(self, parent):
       
        filtre_container = ctk.CTkFrame(parent,height=300,width=270)
        filtre_container.pack(fill="x", padx=10, pady=(0,5))
        filtre_container.pack_propagate(False) 
        
        ctk.CTkLabel(filtre_container, text="Filtreleme", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(20,0))

        self.filtre_frame = ctk.CTkFrame(filtre_container)
        self.filtre_frame.pack(fill="x", expand=True, padx=5, pady=0)

        # --- Grid Yapısı Başlangıcı ---

        # Satır 0: Filtreleme Girdileri
        self.filtre_sutun = ctk.CTkComboBox(self.filtre_frame, state="disabled", width=180, command=self._filtre_sutun_degisti)
        self.filtre_sutun.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky="ew")
        
        self.filtre_operator = ctk.CTkComboBox(self.filtre_frame, state="disabled", width=150, command=self._filtre_operator_degisti)
        self.filtre_operator.grid(row=0, column=1, columnspan=1, padx=5, pady=5, sticky="ew")
        
        self.filtre_giris1 = ctk.CTkEntry(self.filtre_frame, width=150)
        self.filtre_giris1.grid(row=0, column=2, columnspan=1, padx=5, pady=5, sticky="ew")
        self.filtre_giris2 = ctk.CTkEntry(self.filtre_frame, width=150)

        
        # Satır 1: Butonlar (Üst Sıra)
        self.filtre_btn = ctk.CTkButton(self.filtre_frame, text="Filtre Ekle", command=self.filtre_ekle, state=tk.DISABLED)
        self.filtre_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.filtre_temizle_btn = ctk.CTkButton(self.filtre_frame, text="Tüm Filtreleri Temizle", command=self.filtre_temizle, state=tk.DISABLED)
        self.filtre_temizle_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.filtre_sil_btn = ctk.CTkButton(self.filtre_frame, text="Seçili Filtreyi Kaldır", command=self.filtre_sil, state=tk.DISABLED)
        self.filtre_sil_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        # Satır 2: Butonlar (Alt Sıra)
        self.veri_kaydet_btn = ctk.CTkButton(self.filtre_frame, text="Veriyi Kaydet", command=self.veri_kaydet_pencere)
        self.veri_kaydet_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.veri_duzenle_btn = ctk.CTkButton(self.filtre_frame, text="Veri Düzenle", command=self.veri_duzenle_pencere)
        self.veri_duzenle_btn.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Satır 3: Sonuç Etiketi
        self.filtre_sonuc_label = ctk.CTkLabel(self.filtre_frame, text="", anchor="w")

        self.filtre_sonuc_label.grid(row=3, column=0, columnspan=4, padx=5, pady=(10, 5), sticky="ew")

        #Grid Yapısı Sonu
        
        self.filtre_list_frame = ctk.CTkScrollableFrame(filtre_container, label_text="Aktif Filtreler", height=75)
        self.filtre_list_frame.pack(fill="x", padx=5, pady=0)
        self.filtre_widgets = []
        self.selected_filter_index = None

        
        
    def _filtre_paneli_guncelle(self):
        if hasattr(self, 'df') and self.df is not None:
            self.filtre_sutun.configure(state="readonly", values=list(self.df.columns))
            self.filtre_sutun.set("")
            self.filtre_operator.configure(state="readonly", values=["Operatör Seçin"])
            self.filtre_operator.set("Operatör Seçin")
            self.filtre_giris1.delete(0, tk.END)
            self.filtre_giris2.delete(0, tk.END)
            self.filtre_btn.configure(state=tk.NORMAL)
            self.filtre_temizle_btn.configure(state=tk.NORMAL)
            self.filtre_sil_btn.configure(state=tk.NORMAL)
        else:
            self.filtre_sutun.configure(state="disabled", values=[])
            self.filtre_operator.configure(state="disabled", values=[])
            self.filtre_btn.configure(state=tk.DISABLED)
            self.filtre_temizle_btn.configure(state=tk.DISABLED)
            self.filtre_sil_btn.configure(state=tk.DISABLED)

    def _filtre_sutun_degisti(self, secilen_sutun):
        if self.df is None or secilen_sutun not in self.df.columns: return
        yeni_degerler = ["Aralık", "Anahtar Kelime"]
        self.filtre_operator.configure(values=yeni_degerler)
        self.filtre_operator.set(yeni_degerler[0])

    def _filtre_operator_degisti(self, secilen_operator):
        if secilen_operator == 'Aralık':
            # 'Aralık' seçildiğinde ikinci giriş kutusunu 0. satır 3. sütuna ekle
            self.filtre_giris2.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        else:
            self.filtre_giris2.grid_forget()

    def _parse_date(self, date_str):
        """Farklı tarih formatlarını ayrıştırır"""
        if not date_str or pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        
        #Farklı tarih formatlarını dene
        date_formats = [
            '%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%d.%m.%y', '%d-%m-%y', '%y-%m-%d', '%d/%m/%y',
            '%d.%m.%Y', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        
        #Genel tarih ayrıştırma
        try:
            return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
        except:
            return None

    def _kolon_tipi_bul(self, col):
        seri = self.df[col].dropna().astype(str)
        if seri.empty: return 'metin'
        
        # Tarih formatlarını test et
        try:
            # Farklı tarih formatlarını dene
            test_seri = seri.iloc[:min(10, len(seri))]
            for date_format in ['%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d.%m.%y', '%d-%m-%y']:
                try:
                    pd.to_datetime(test_seri, format=date_format, errors='raise')
                    return 'tarih'
                except:
                    continue
            # Genel tarih algılama (uyarılar için)
            try:
                pd.to_datetime(test_seri, dayfirst=True, errors='coerce')
                # Eğer en az %50'si başarılı parse edildiyse tarih olarak kabul et .
                if pd.to_datetime(test_seri, dayfirst=True, errors='coerce').notna().sum() >= len(test_seri) * 0.5:
                    return 'tarih'
            except:
                pass
        except Exception: pass
        
        try:
            pd.to_numeric(seri.str.replace(r'[^0-9,.-]', '', regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='raise')
            return 'sayi'
        except Exception: pass
        return 'metin'

    def filtre_ekle(self):
        col = self.filtre_sutun.get()
        op = self.filtre_operator.get()
        val1 = self.filtre_giris1.get()
        val2 = self.filtre_giris2.get() if op == 'Aralık' else None
        if not col or op == "Operatör Seçin" or not val1 or (op == 'Aralık' and not val2):
            messagebox.showwarning("Uyarı", "Lütfen tüm filtre alanlarını doğru şekilde doldurun.")
            return
        tip = self._kolon_tipi_bul(col)
        self.filtreler.append((col, op, val1, val2, tip))
        self._filtre_listbox_guncelle()
        self._filtreleri_uygula()

    def _filtre_listbox_guncelle(self):
        for widget in self.filtre_widgets: widget.destroy()
        self.filtre_widgets.clear()
        self.selected_filter_index = None
        for i, (col, op, val1, val2, _) in enumerate(self.filtreler):
            text = f"{col} {op}: {val1} - {val2}" if op == 'Aralık' else f"{col} {op}: {val1}"
            label = ctk.CTkButton(self.filtre_list_frame, text=text, anchor="w", fg_color="transparent", 
                                  command=lambda index=i: self._on_filter_select(index))
            
            label.pack(fill="x", padx=5, pady=2)
            self.filtre_widgets.append(label)

    def _on_filter_select(self, index):
        self.selected_filter_index = index
        for i, widget in enumerate(self.filtre_widgets):
            widget.configure(font=ctk.CTkFont(weight="bold" if i == index else "normal"))

    def filtre_sil(self):
        if self.selected_filter_index is None:
            messagebox.showwarning("Uyarı", "Lütfen kaldırmak için bir filtre seçin.")
            return
        self.filtreler.pop(self.selected_filter_index)
        self._filtre_listbox_guncelle()
        self._filtreleri_uygula()

    def filtre_temizle(self):
        self.filtreler.clear()
        self._filtre_listbox_guncelle()
        self._filtreleri_uygula()

    def _filtreleri_uygula(self):
        if self.df is None: return
        if not self.filtreler:
            self.df_filtered = None
            self._tabloyu_goster(self.df)
            self.filtre_sonuc_label.configure(text=f"Toplam satır: {len(self.df)}")
            return
        df = self.df.copy()
        try:
            for col, op, val1, val2, tip in self.filtreler:
                if op == 'Aralık':
                    if tip == 'tarih':
                        # Farklı tarih formatlarını dene
                        v1 = self._parse_date(val1)
                        v2 = self._parse_date(val2)
                        if v1 is not None and v2 is not None:
                            df_col_dates = pd.to_datetime(df[col], errors='coerce')
                            df = df[df_col_dates.between(v1, v2)]
                    else:
                        col_numeric = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d,.-]', '', regex=True).str.replace(',', '.', regex=True), errors='coerce')
                        v1 = float(str(val1).replace('.', '').replace(',', '.'))
                        v2 = float(str(val2).replace('.', '').replace(',', '.'))
                        df = df[col_numeric.between(v1, v2)]
                elif op == 'Anahtar Kelime':
                    keywords = [k.strip().lower() for k in re.split(r',| ve | ya da | veya ', val1) if k.strip()]
                    mask = df[col].astype(str).str.lower().apply(lambda x: all(kw in x for kw in keywords))
                    df = df[mask]
            self.df_filtered = df
            self._tabloyu_goster(df)
            self.filtre_sonuc_label.configure(text=f"Filtreli satır: {len(df)} / Toplam: {len(self.df)}")
        except Exception as e:
            messagebox.showerror("Filtreleme Hatası", f"Filtre uygulanamadı:\n{e}")