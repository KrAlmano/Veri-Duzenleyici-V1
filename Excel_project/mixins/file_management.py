import os
import shutil
import pandas as pd
from tkinter import filedialog, messagebox, simpledialog
from config import DATABASE_DIR

class FileManagementMixin:
    def _dosya_agacini_guncelle(self):
        self.dosya_tree.delete(*self.dosya_tree.get_children())
        if not os.path.exists(DATABASE_DIR):
            os.makedirs(DATABASE_DIR)
        for klasor in sorted(os.listdir(DATABASE_DIR)):
            klasor_yol = os.path.join(DATABASE_DIR, klasor)
            if os.path.isdir(klasor_yol):
                kid = self.dosya_tree.insert('', 'end', text=klasor, open=True)
                for dosya in sorted(os.listdir(klasor_yol)):
                    if dosya.endswith(('.xlsx', '.csv')):
                        self.dosya_tree.insert(kid, 'end', text=dosya, values=(os.path.join(klasor, dosya),))

    def dosya_yukle(self):
        dosya = filedialog.askopenfilename(title="Dosya Seç", filetypes=[
            ("Excel Dosyaları", "*.xlsx"),
            ("CSV Dosyaları", "*.csv"),
            ("Tüm Dosyalar", "*.*")
        ])
        if not dosya:
            return
        dosya_adi = os.path.basename(dosya)
        ana_isim = os.path.splitext(dosya_adi)[0]
        hedef_klasor = os.path.join(DATABASE_DIR, ana_isim)
        if not os.path.exists(hedef_klasor):
            os.makedirs(hedef_klasor)
        hedef_yol = os.path.join(hedef_klasor, dosya_adi)
        try:
            shutil.copy2(dosya, hedef_yol)
            messagebox.showinfo("Başarılı", f"{dosya_adi} başarıyla yüklendi.")
            self._dosya_agacini_guncelle()
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenemedi:\n{e}")

    def _dosya_agacinda_secildi(self, event):
        secim = self.dosya_tree.selection()
        if not secim:
            return
        item = self.dosya_tree.item(secim[0])
        parent = self.dosya_tree.parent(secim[0])
        if parent:  # Dosya seçildi
            klasor = self.dosya_tree.item(parent)['text']
            dosya_adi = item['text']
            dosya_yolu = os.path.join(DATABASE_DIR, klasor, dosya_adi)
            self.secili_klasor = klasor
            self.secili_dosya = dosya_adi
            try:
                # Dosya uzantısına göre okuma yöntemini belirle
                if dosya_adi.lower().endswith('.csv'):
                    df = pd.read_csv(dosya_yolu, encoding='utf-8')
                else:
                    df = pd.read_excel(dosya_yolu, engine="openpyxl")
                
                df = df.dropna(how='all')
                if any([str(col).startswith('Unnamed') for col in df.columns]):
                    new_header = df.iloc[0]
                    df = df[1:]
                    df.columns = new_header
                    df = df.reset_index(drop=True)
                self.df = df
                self.df_filtered = None
                self.filtreler = []
                self._tabloyu_goster(df)
                self._filtre_paneli_guncelle()
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı:\n{e}")
        else:
            self.secili_klasor = item['text']
            self.secili_dosya = None
            
    def _treeview_sag_tik_menu(self, event):
        iid = self.dosya_tree.identify_row(event.y)
        if iid:
            self.dosya_tree.selection_set(iid)
            try:
                self.sag_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.sag_menu.grab_release()
        else:
            return

    def _dosya_sil(self):
        secim = self.dosya_tree.selection()
        if not secim or len(secim) != 1:
            messagebox.showwarning("Uyarı!", "Lütfen silmek için bir dosya veya klasör seçin.")
            return
        item = self.dosya_tree.item(secim[0])
        parent = self.dosya_tree.parent(secim[0])
        if parent:  # Dosya sil
            klasor = self.dosya_tree.item(parent)['text']
            dosya_adi = item['text']
            dosya_yolu = os.path.join(DATABASE_DIR, klasor, dosya_adi)
            if messagebox.askyesno("Sil", f"{dosya_adi} dosyasını silmek istediğinize emin misiniz?"):
                try:
                    os.remove(dosya_yolu)
                    self._dosya_agacini_guncelle()
                except Exception as e:
                    messagebox.showerror("Hata", f"Dosya silinemedi:\n{e}")
        else:  # Klasör sil
            klasor = item['text']
            klasor_yolu = os.path.join(DATABASE_DIR, klasor)
            if messagebox.askyesno("Sil", f"{klasor} klasörünü ve içindeki tüm dosyaları silmek istediğinize emin misiniz?"):
                try:
                    shutil.rmtree(klasor_yolu)
                    self._dosya_agacini_guncelle()
                except Exception as e:
                    messagebox.showerror("Hata", f"Klasör silinemedi:\n{e}")

    def _dosya_yeniden_adlandir(self):
        secim = self.dosya_tree.selection()
        if not secim or len(secim) != 1:
            messagebox.showwarning("Uyarı", "Lütfen yeniden adlandırmak için bir dosya veya klasör seçin.")
            return
        item = self.dosya_tree.item(secim[0])
        parent = self.dosya_tree.parent(secim[0])
        if parent:  # Dosya yeniden adlandır
            klasor = self.dosya_tree.item(parent)['text']
            eski_ad = item['text']
            yeni_ad = simpledialog.askstring("Yeniden Adlandır", f"Yeni dosya adını girin (uzantı dahil):", initialvalue=eski_ad)
            if yeni_ad and yeni_ad != eski_ad:
                eski_yol = os.path.join(DATABASE_DIR, klasor, eski_ad)
                yeni_yol = os.path.join(DATABASE_DIR, klasor, yeni_ad)
                try:
                    os.rename(eski_yol, yeni_yol)
                    self._dosya_agacini_guncelle()
                except Exception as e:
                    messagebox.showerror("Hata", f"Dosya yeniden adlandırılamadı:\n{e}")
        else:  # Klasör yeniden adlandır
            eski_klasor = item['text']
            yeni_klasor = simpledialog.askstring("Yeniden Adlandır", f"Yeni klasör adını girin:", initialvalue=eski_klasor)
            if yeni_klasor and yeni_klasor != eski_klasor:
                eski_yol = os.path.join(DATABASE_DIR, eski_klasor)
                yeni_yol = os.path.join(DATABASE_DIR, yeni_klasor)
                try:
                    os.rename(eski_yol, yeni_yol)
                    self._dosya_agacini_guncelle()
                except Exception as e:
                    messagebox.showerror("Hata", f"Klasör yeniden adlandırılamadı:\n{e}")