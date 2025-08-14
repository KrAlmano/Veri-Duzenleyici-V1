import customtkinter as ctk
import pandas as pd
import re
from tkinter import messagebox


class DataEditorMixin:
    def veri_duzenle_pencere(self):
        if self.df is None:
            
            messagebox.showwarning("Uyarı", "Düzenlenecek veri yüklenmemiş.")
            return

        df_orjinal_kopya = self.df.copy()
        
        pencere = ctk.CTkToplevel(self)
        pencere.title("Veri Düzenle")
        pencere.geometry("800x500")

        if self.df is None and self.df_filtered is None:
            
            messagebox.showwarning("Uyarı", "Düzenlenecek veri yok.")
            return
            
        df = self.df_filtered if self.df_filtered is not None else self.df
        
        # Filtre paneli
        filtre_frame = ctk.CTkFrame(pencere)
        filtre_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(filtre_frame, text="Filtreleme (Geçici)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        filtre_kontroller_frame = ctk.CTkFrame(filtre_frame)
        filtre_kontroller_frame.pack(fill="x", padx=10, pady=5)
        
        filtre_sutun = ctk.CTkComboBox(filtre_kontroller_frame, state="readonly", width=200, values=list(df.columns))
        filtre_sutun.pack(side="left", padx=5, pady=5)
        
        filtre_tur = ctk.CTkComboBox(filtre_kontroller_frame, state="readonly", width=150, values=["Aralık", "Anahtar Kelime"])
        filtre_tur.pack(side="left", padx=5, pady=5)
        
        filtre_giris1 = ctk.CTkEntry(filtre_kontroller_frame, width=150, placeholder_text="Değer 1")
        filtre_giris1.pack(side="left", padx=5, pady=5)
        
        filtre_giris2 = ctk.CTkEntry(filtre_kontroller_frame, width=150, placeholder_text="Değer 2")
        filtre_giris2.pack(side="left", padx=5, pady=5)
        filtre_giris2.pack_forget()
        
        def filtre_tur_degisti(evt):
            tur = filtre_tur.get()
            if tur == "Aralık":
                filtre_giris2.pack(side="left", padx=5, pady=5)
                filtre_giris1.delete(0, "end")
                filtre_giris2.delete(0, "end")
                filtre_giris1.configure(width=150)
                filtre_giris2.configure(width=150)
            else:
                filtre_giris2.pack_forget()
                filtre_giris1.delete(0, "end")
                filtre_giris1.configure(width=300)
                
        # Başlangıçta filtre türü değişikliğini tetikle
        filtre_tur.bind('<<ComboboxSelected>>', filtre_tur_degisti)
        
        # Başlangıçta "Aralık" seçili olsun ve ikinci giriş kutusu görünsün
        filtre_tur.set("Aralık")
        filtre_giris2.pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(filtre_kontroller_frame, text="Filtrele", command=lambda: satirlari_guncelle()).pack(side="left", padx=5, pady=5)
        
        # Sıralama kontrolleri
        siralama_frame = ctk.CTkFrame(filtre_frame)
        siralama_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(siralama_frame, text="Sıralama:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5, pady=5)
        
        # Tarih sütunlarını sıralamadan çıkar
        if hasattr(self, '_kolon_tipi_bul'):
            siralanabilir_kolonlar = [c for c in df.columns if self._kolon_tipi_bul(c) != 'tarih']
        else:
            siralanabilir_kolonlar = list(df.columns)
        siralama_sutun = ctk.CTkComboBox(siralama_frame, values=siralanabilir_kolonlar, state="readonly", width=150)
        siralama_sutun.pack(side="left", padx=5, pady=5)
        
        siralama_yonu = ctk.CTkComboBox(siralama_frame, values=["Artan", "Azalan"], state="readonly", width=100)
        siralama_yonu.set("Artan")
        siralama_yonu.pack(side="left", padx=5, pady=5)
        
        def siralama_uygula():
            nonlocal gosterilen_indexler
            col = siralama_sutun.get()
            yon = siralama_yonu.get()
            
            if not col:
                messagebox.showwarning("Uyarı", "Lütfen sıralama için bir sütun seçin.")
                return
            # Tarih sütunu seçildiyse güvenlik için iptal et (teoride listede yok)
            if hasattr(self, '_kolon_tipi_bul') and self._kolon_tipi_bul(col) == 'tarih':
                messagebox.showwarning("Uyarı", "Tarih sütunları sıralama dışıdır.")
                return
                
            try:
                # Mevcut filtrelenmiş veriyi al
                temp_df = df.copy()
                
                # Eğer filtre uygulanmışsa, filtrelenmiş veriyi kullan
                if filtre_sutun.get() and filtre_tur.get():
                    # Filtreleme mantığını tekrarla
                    col_filter = filtre_sutun.get()
                    tur_filter = filtre_tur.get()
                    val1_filter = filtre_giris1.get().strip()
                    val2_filter = filtre_giris2.get().strip() if tur_filter == "Aralık" else None
                    
                    if tur_filter == "Aralık" and (not val1_filter or not val2_filter):
                        messagebox.showwarning("Uyarı", "Aralık filtrelemesi için her iki değeri de girin.")
                        return
                    elif tur_filter == "Anahtar Kelime" and not val1_filter:
                        messagebox.showwarning("Uyarı", "Anahtar kelime filtrelemesi için değer girin.")
                        return
                    
                    # Filtreleme uygula
                    if tur_filter == "Aralık":
                        seri = temp_df[col_filter].dropna().astype(str)
                        if not seri.empty:
                            try:
                                test_seri = seri.iloc[:min(10, len(seri))]
                                tip = 'metin'
                                for date_format in ['%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d.%m.%y', '%d-%m-%y']:
                                    try:
                                        pd.to_datetime(test_seri, format=date_format, errors='raise')
                                        tip = 'tarih'
                                        break
                                    except:
                                        continue
                                else:
                                    try:
                                        pd.to_datetime(test_seri, dayfirst=True, errors='raise')
                                        tip = 'tarih'
                                    except Exception:
                                        try:
                                            pd.to_numeric(seri.str.replace(r'[^0-9,.-]', '', regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='raise')
                                            tip = 'sayi'
                                        except Exception:
                                            tip = 'metin'
                                
                                if tip == 'tarih':
                                    v1 = _parse_date_editor(val1_filter)
                                    v2 = _parse_date_editor(val2_filter)
                                    if v1 is not None and v2 is not None:
                                        df_col_dates = pd.to_datetime(temp_df[col_filter], errors='coerce')
                                        temp_df = temp_df[df_col_dates.between(v1, v2)]
                                    else:
                                        messagebox.showerror("Hata", "Tarih formatı tanınmadı.")
                                        return
                                else:
                                    temp_df[col_filter] = temp_df[col_filter].astype(str).str.replace(r'[^0-9,.-]', '', regex=True)
                                    temp_df[col_filter] = temp_df[col_filter].str.replace('.', '', regex=False)
                                    temp_df[col_filter] = temp_df[col_filter].str.replace(',', '.', regex=False)
                                    temp_df[col_filter] = pd.to_numeric(temp_df[col_filter], errors='coerce')
                                    v1 = float(val1_filter.replace('.', '').replace(',', '.'))
                                    v2 = float(val2_filter.replace('.', '').replace(',', '.'))
                                    temp_df = temp_df[(temp_df[col_filter] >= v1) & (temp_df[col_filter] <= v2)]
                            except Exception as e:
                                messagebox.showerror("Filtreleme Hatası", f"Hata: {str(e)}")
                                return
                    else:
                        keywords = re.split(r',| ve | ya da | veya ', val1_filter)
                        keywords = [k.strip() for k in keywords if k.strip()]
                        mask = temp_df[col_filter].astype(str).apply(lambda x: all(kw.lower() in x.lower() for kw in keywords))
                        temp_df = temp_df[mask]
                
                # Sıralama uygula
                ascending = yon == "Artan"
                
                # Sütun tipini belirle
                seri = temp_df[col].dropna().astype(str)
                if not seri.empty:
                    try:
                        test_seri = seri.iloc[:min(10, len(seri))]
                        tip = 'metin'
                        for date_format in ['%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d.%m.%y', '%d-%m-%y']:
                            try:
                                pd.to_datetime(test_seri, format=date_format, errors='raise')
                                tip = 'tarih'
                                break
                            except:
                                continue
                        else:
                            try:
                                pd.to_datetime(test_seri, dayfirst=True, errors='raise')
                                tip = 'tarih'
                            except Exception:
                                try:
                                    pd.to_numeric(seri.str.replace(r'[^0-9,.-]', '', regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='raise')
                                    tip = 'sayi'
                                except Exception:
                                    tip = 'metin'
                        
                        if tip == 'tarih':
                             # Tarih sütunu için özel sıralama
                             temp_df[col] = pd.to_datetime(temp_df[col], errors='coerce')
                             temp_df = temp_df.sort_values(by=col, ascending=ascending, na_position='last')
                             temp_df[col] = temp_df[col].dt.strftime('%d.%m.%Y')
                        elif tip == 'sayi':
                            # Sayı sütunu için özel sıralama
                            temp_df[col] = pd.to_numeric(temp_df[col].astype(str).str.replace(r'[^\d,.-]', '', regex=True).str.replace(',', '.', regex=True), errors='coerce')
                            temp_df = temp_df.sort_values(by=col, ascending=ascending, na_position='last')
                        else:
                            # Metin sütunu için normal sıralama
                            temp_df = temp_df.sort_values(by=col, ascending=ascending, na_position='last')
                    except Exception as e:
                        messagebox.showerror("Sıralama Hatası", f"Sıralama hatası: {str(e)}")
                        return
                
                # Sonuçları göster
                satir_listbox.delete(0, "end")
                gosterilen_indexler = list(temp_df.index)
                for i, row in temp_df.iterrows():
                    satir_listbox.insert("end", f"{i}: {list(row)}")
                    
                messagebox.showinfo("Başarılı", f"Veriler {col} sütununa göre {yon.lower()} sıralandı.")
                
            except Exception as e:
                messagebox.showerror("Sıralama Hatası", f"Sıralama uygulanırken hata oluştu:\n{str(e)}")
        
        ctk.CTkButton(siralama_frame, text="Sırala", command=siralama_uygula).pack(side="left", padx=5, pady=5)
        
        # Satır listesi
        satir_frame = ctk.CTkFrame(pencere)
        satir_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        ctk.CTkLabel(satir_frame, text="Satır Seç:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        # Listbox için tkinter kullanmaya devam ediyoruz
        import tkinter as tk
        
        satir_listbox = tk.Listbox(satir_frame, width=120, height=8, bg="#2b2b2b", fg="white", selectbackground="#1f538d")
        satir_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        
        gosterilen_indexler = list(df.index)
        
        def _parse_date_editor(date_str):
            """Farklı tarih formatlarını ayrıştırır"""
            if not date_str or pd.isna(date_str):
                return None
            
            date_str = str(date_str).strip()
            
            # Farklı tarih formatlarını dene
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
            
            # Genel tarih ayrıştırma (dayfirst=True ile)
            try:
                return pd.to_datetime(date_str, dayfirst=True, errors='coerce')
            except:
                return None

        def satirlari_guncelle():
            nonlocal gosterilen_indexler
            temp_df = df.copy()
            col = filtre_sutun.get()
            tur = filtre_tur.get()
            val1 = filtre_giris1.get().strip()
            val2 = filtre_giris2.get().strip() if tur == "Aralık" else None
            
            # Filtreleme koşullarını kontrol et
            if not col or not tur:
                # Hiçbir filtre yoksa tüm verileri göster
                satir_listbox.delete(0, "end")
                gosterilen_indexler = list(temp_df.index)
                for i, row in temp_df.iterrows():
                    satir_listbox.insert("end", f"{i}: {list(row)}")
                return
            
            if tur == "Aralık" and (not val1 or not val2):
                # Aralık seçilmiş ama değerler eksik
                messagebox.showwarning("Uyarı", "Aralık filtrelemesi için her iki değeri de girin.")
                return
            elif tur == "Anahtar Kelime" and not val1:
                # Anahtar kelime seçilmiş ama değer yok
                messagebox.showwarning("Uyarı", "Anahtar kelime filtrelemesi için değer girin.")
                return
            
            try:
                if tur == "Aralık":
                    # Sütun tipini belirle
                    seri = temp_df[col].dropna().astype(str)
                    if seri.empty:
                        tip = 'metin'
                    else:
                        # Tarih formatlarını test et
                        try:
                            test_seri = seri.iloc[:min(10, len(seri))]
                            for date_format in ['%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%d.%m.%y', '%d-%m-%y']:
                                try:
                                    pd.to_datetime(test_seri, format=date_format, errors='raise')
                                    tip = 'tarih'
                                    break
                                except:
                                    continue
                            else:
                                # Genel tarih algılama
                                pd.to_datetime(test_seri, dayfirst=True, errors='raise')
                                tip = 'tarih'
                        except Exception:
                            try:
                                pd.to_numeric(seri.str.replace(r'[^0-9,.-]', '', regex=True).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='raise')
                                tip = 'sayi'
                            except Exception:
                                tip = 'metin'
                    
                    if tip == 'tarih':
                        # Tarih aralığı filtreleme
                        v1 = _parse_date_editor(val1)
                        v2 = _parse_date_editor(val2)
                        if v1 is not None and v2 is not None:
                            df_col_dates = pd.to_datetime(temp_df[col], errors='coerce')
                            temp_df = temp_df[df_col_dates.between(v1, v2)]
                        else:
                            messagebox.showerror("Hata", "Tarih formatı tanınmadı. Lütfen geçerli bir tarih formatı kullanın.")
                            return
                    else:
                        # Sayısal aralık filtreleme
                        temp_df[col] = temp_df[col].astype(str).str.replace(r'[^0-9,.-]', '', regex=True)
                        temp_df[col] = temp_df[col].str.replace('.', '', regex=False)
                        temp_df[col] = temp_df[col].str.replace(',', '.', regex=False)
                        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
                        v1 = float(val1.replace('.', '').replace(',', '.'))
                        v2 = float(val2.replace('.', '').replace(',', '.'))
                        temp_df = temp_df[(temp_df[col] >= v1) & (temp_df[col] <= v2)]
                else:
                    # Anahtar kelime filtreleme
                    keywords = re.split(r',| ve | ya da | veya ', val1)
                    keywords = [k.strip() for k in keywords if k.strip()]
                    mask = temp_df[col].astype(str).apply(lambda x: all(kw.lower() in x.lower() for kw in keywords))
                    temp_df = temp_df[mask]
                
                # Sonuçları göster
                satir_listbox.delete(0, "end")
                gosterilen_indexler = list(temp_df.index)
                for i, row in temp_df.iterrows():
                    satir_listbox.insert("end", f"{i}: {list(row)}")
                
                # Sonuç sayısını göster
                if len(temp_df) == 0:
                    messagebox.showinfo("Bilgi", "Filtreleme kriterlerine uygun veri bulunamadı.")
                    
            except Exception as e:
                messagebox.showerror("Filtreleme Hatası", f"Filtre uygulanırken hata oluştu:\n{str(e)}")
                print(f"Filtreleme hatası: {e}")
                
        satirlari_guncelle()
        
        # Entryler - Yatay kaydırma ile
        duzen_frame = ctk.CTkFrame(pencere, height=120)
        duzen_frame.pack(pady=5, padx=10, fill="x")
        duzen_frame.pack_propagate(False) # Yüksekliğin sabit kalmasını sağlar
        # Canvas ve scrollbar için frame
        canvas_frame = ctk.CTkFrame(duzen_frame)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=1)
        
        # Canvas oluştur
        import tkinter as tk
        canvas = tk.Canvas(canvas_frame, bg="#2b2b2b", highlightthickness=0)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        
        # İçerik frame'i
        content_frame = ctk.CTkFrame(canvas)
        
        # Canvas'ı yapılandır
        canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Scrollbar'ları yerleştir
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # İçerik frame'ini canvas'a ekle
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Canvas boyutunu güncelle
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Canvas genişliğini içerik genişliğine ayarla
            canvas.itemconfig(canvas_window, width=max(content_frame.winfo_reqwidth(), canvas.winfo_width()))
        
        content_frame.bind("<Configure>", configure_scroll_region)
        
        # Canvas boyutunu pencere boyutuna göre ayarla
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=max(content_frame.winfo_reqwidth(), event.width))
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        entryler = []
        for idx, col in enumerate(df.columns):
            ctk.CTkLabel(content_frame, text=col).grid(row=0, column=idx, padx=5, pady=5)
            e = ctk.CTkEntry(content_frame, width=150)
            e.grid(row=1, column=idx, padx=5, pady=5)
            entryler.append(e)
            
        def ekle():
            values = [e.get() for e in entryler]
            new_row = pd.DataFrame([values], columns=df.columns)
            df.loc[len(df)] = values
            satirlari_guncelle()
            for e in entryler:
                e.delete(0, "end")
                
        def sil():
            selection = satir_listbox.curselection()
            if selection:
                idx = gosterilen_indexler[selection[0]]
                df.drop(idx, inplace=True)
                df.reset_index(drop=True, inplace=True)
                satirlari_guncelle()
                
        def guncelle():
            selection = satir_listbox.curselection()
            if selection:
                idx = gosterilen_indexler[selection[0]]
                values = [e.get() for e in entryler]
                for i, col in enumerate(df.columns):
                    df.loc[idx, col] = values[i]
                satirlari_guncelle()
                for e in entryler:
                    e.delete(0, "end")
                    
        def satir_secildi(event):
            selection = satir_listbox.curselection()
            if selection:
                idx = gosterilen_indexler[selection[0]]
                row = df.loc[idx]
                for i, e in enumerate(entryler):
                    e.delete(0, "end")
                    e.insert(0, str(row.iloc[i]))
                    
        satir_listbox.bind('<<ListboxSelect>>', satir_secildi)
        
        # Butonlar
        buton_frame = ctk.CTkFrame(pencere)
        buton_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(buton_frame, text="Ekle", command=ekle).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(buton_frame, text="Sil", command=sil).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(buton_frame, text="Güncelle", command=guncelle).pack(side="left", padx=5, pady=5)
        
        def kaydet():
            if self.df_filtered is not None:
                self.df_filtered = df
            else:
                self.df = df
            self._tabloyu_goster(df)
            from tkinter import messagebox
            messagebox.showinfo("Başarılı", "Veri güncellendi.")
            pencere.destroy()
            
        ctk.CTkButton(buton_frame, text="Kaydet", command=kaydet).pack(side="right", padx=5, pady=5)