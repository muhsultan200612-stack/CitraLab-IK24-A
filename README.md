# CitraLab — Aplikasi Pengolahan Citra Digital
### Proyek Akhir IK24

---

## 📦 Instalasi

Pastikan Python 3.8+ sudah terinstall, lalu jalankan:

```bash
pip install -r requirements.txt
```

## ▶ Cara Menjalankan

```bash
python main.py
```

---

## 🗂 Fitur Aplikasi

### ✅ Fitur Wajib (40 poin)
| Fitur | Lokasi di App |
|---|---|
| Input Gambar | Tombol "Buka Gambar" di header |
| Tampilkan Gambar | Tab "🖼 Tampilkan" |
| Grayscale | Tab "⚙ Proses Dasar" → Tombol Grayscale |
| Citra Biner | Tab "⚙ Proses Dasar" → Tombol Biner |
| Operasi Aritmatika | Tab "➕ Aritmatika & Logika" |
| Operasi Logika | Tab "➕ Aritmatika & Logika" |
| Tampilkan Hasil | Setiap tab menampilkan Output |

### ⭐ Fitur Optional
| Fitur | Poin | Lokasi |
|---|---|---|
| Histogram | 10 poin | Tab "📊 Histogram" |
| Konvolusi / Filter | 20 poin | Tab "🔍 Konvolusi / Filter" |
| Morfologi | 30 poin | Tab "🔬 Morfologi" |

---

## 📋 Penjelasan Fitur

### Proses Dasar
- **Grayscale**: Konversi gambar BGR ke abu-abu
- **Biner**: Threshold dengan nilai yang bisa diatur (0–255)

### Aritmatika
- **Penjumlahan**: Menambah nilai piksel (mencerahkan)
- **Pengurangan**: Mengurangi nilai piksel (menggelapkan)
- **Perkalian**: Mengalikan piksel (kontras)
- **Pembagian**: Membagi piksel (mengurangi kontras)

### Logika
- **AND, OR, NOT, XOR**: Operasi bitwise pada citra biner

### Histogram
- Menampilkan distribusi intensitas piksel
- Mendukung gambar RGB (3 channel) dan Grayscale

### Konvolusi / Filter
- **Gaussian Blur**: Menghaluskan gambar
- **Sharpening**: Mempertajam tepi
- **Sobel Edge Detection**: Mendeteksi tepi horizontal+vertikal
- **Laplacian**: Mendeteksi tepi semua arah
- **Emboss**: Efek emboss/timbul

### Morfologi (dengan 4 pilihan SE)
- **Dilasi**: Memperbesar objek putih
- **Erosi**: Memperkecil objek putih
- **Opening**: Erosi kemudian Dilasi
- **Closing**: Dilasi kemudian Erosi
- SE tersedia: Rectangle, Ellipse, Cross, Diamond

---

## 💾 Simpan Hasil
Tombol "Simpan Hasil" di header → pilih lokasi & format (PNG/JPG)

## 🔄 Reset
Tombol "Reset" → mengembalikan gambar ke aslinya
