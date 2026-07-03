# Veri-Duzenleyici-V1
# Veri Düzenleyici V1

CustomTkinter ile geliştirilmiş, Excel/CSV dosyalarını görsel bir arayüzden filtrelemeyi,
düzenlemeyi ve Excel/Word/CSV formatlarında dışa aktarmayı sağlayan bir masaüstü veri
yönetim uygulaması.

## Özellikler

- **Dosya yönetimi:** Excel (`.xlsx`) ve CSV dosyalarını yükleyip otomatik olarak
  organize eden bir klasör yapısında saklama, silme, yeniden adlandırma
- **Otomatik kolon tipi algılama:** Her kolonun tarih, sayı veya metin olduğunu otomatik
  tanıyor (Türkçe sayı formatı `1.234,56` ve farklı tarih ayraçları `.`/`-`/`/` dahil)
- **Filtreleme:** Aralık (min-max) ve anahtar kelime (`ve`/`veya`/`ya da` bağlaçlarıyla
  çoklu kelime) bazlı filtreleme
- **Sıralama:** Artan/azalan, kolon tipine duyarlı sıralama
- **Satır düzenleme:** Ekleme, silme, güncelleme
- **Dışa aktarma:** Excel, Word (`.docx`, tablo formatında, kolon seçimli) veya CSV olarak
  kaydetme

## Ekran Görüntüsü

> _Buraya uygulamanın 1-2 ekran görüntüsünü ekle (ör. ana ekran + filtre paneli)._

## Kullanılan Teknolojiler

- Python 3
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern görünümlü GUI
- [pandas](https://pandas.pydata.org/) — veri işleme
- [openpyxl](https://openpyxl.readthedocs.io/) — Excel okuma/yazma
- [python-docx](https://python-docx.readthedocs.io/) — Word dışa aktarımı

## Kurulum

```bash
git clone https://github.com/KrAlmano/Veri-Duzenleyici-V1.git
cd Veri-Duzenleyici-V1/Excel_project
pip install customtkinter pandas openpyxl python-docx
```

## Çalıştırma

```bash
python main.py
```

Uygulama açıldığında, yüklediğin dosyalar `~/Desktop/Veri Düzenleyici VeriTabanı` klasörü
altında otomatik olarak organize edilir.

## Proje Yapısı

```
Excel_project/
├── main.py                  # Giriş noktası
├── config.py                # Veritabanı klasör yolu ayarı
├── app.py                   # Ana pencere sınıfı
└── mixins/
    ├── ui_parts.py           # Arayüz iskeleti ve tema
    ├── file_management.py    # Dosya/klasör işlemleri
    ├── filtering.py           # Filtreleme ve kolon tipi algılama
    ├── data_editor.py         # Satır düzenleme penceresi
    └── data_export.py         # Excel/Word/CSV dışa aktarma
```

## Bilinen Sınırlamalar

- Kolon tipi algılama mantığı henüz tek bir yerde merkezi değil (geliştirme aşamasında)
- Test kapsamı henüz yok
- Şu an için `~/Desktop` altında sabit bir klasör yapısı kullanıyor

## Lisans

Bu proje [LICENSE](./LICENSE) dosyasında belirtilen lisans altında sunulmaktadır.
