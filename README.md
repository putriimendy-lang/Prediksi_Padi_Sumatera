# PadiPredict — Prediksi Hasil Produksi Padi di Pulau Sumatera

Aplikasi web berbasis Django untuk melihat data produksi padi di Pulau Sumatera, membandingkan hasil antarprovinsi, dan memperkirakan produksi padi menggunakan machine learning serta asisten AI.

## Masalah yang diselesaikan
Produksi padi merupakan komoditas pangan strategis yang hasilnya sangat dipengaruhi oleh luas panen dan faktor iklim (curah hujan, kelembapan, serta suhu udara). PadiPredict dibuat untuk memudahkan pemantauan data historis produksi padi antarprovinsi di Pulau Sumatera sekaligus menyediakan estimasi hasil produksi secara cepat berbasis data historis.

## Dataset
- **Sumber:** [Dataset Tanaman Padi Sumatera — Kaggle (Ardika Satria)](https://www.kaggle.com/datasets/ardikasatria/datasettanamanpadisumatera)
- **Lisensi:** `[Isi sesuai lisensi di halaman Kaggle]`
- **Jumlah data:** 224 baris dan 7 kolom (data 8 provinsi di Pulau Sumatera, tahun 1993–2020)
- **Lokasi berkas:** `dataset/Data_Tanaman_Padi_Sumatera.csv` (database SQLite proyek berada di `db.sqlite3`)

## Metode
- **Algoritma Machine Learning:** Perbandingan dua model regresi, yaitu **Linear Regression** dan **Random Forest Regressor** menggunakan `scikit-learn`.
- **Pembagian Data (Split):** Pembagian berbasis waktu (*time-based split*) melalui `ml_model/training_model.py`:
  - **Data latih (Train):** Data hingga tahun 2015.
  - **Data uji (Test):** Data mulai tahun 2016.
- **Fitur Tambahan:** Integrasi Asisten AI berbasis Google Gemini (opsional melalui `GEMINI_API_KEY`) dan pengelolaan data melalui Django Admin.
- **Teknologi:** Python 3.14.6, Django 6.1.3, SQLite, pandas, NumPy, scikit-learn, joblib, matplotlib, dan seaborn.

## Hasil & evaluasi

Pengujian dilakukan pada data mulai tahun 2016 menggunakan tiga metrik, yaitu MAE, RMSE, dan R². Hasil lengkapnya tersimpan di `ml_model/hasil_evaluasi.csv`.

Ringkasan hasil pengujian:
- **Linear Regression:** MAE = 0,00 | RMSE = 0,00 | R² = 0,00
- **Random Forest:** MAE = 0,00 | RMSE = 0,00 | R² = 0,00

*(Ganti angka 0,00 di atas dengan angka asli dari file `ml_model/hasil_evaluasi.csv` sebelum dikumpulkan).*

## Refleksi singkat

Dari pengerjaan proyek ini, alur aplikasi dari pengelolaan dataset, pelatihan dua model regresi, sampai menampilkan hasil prediksi dan evaluasi di web Django sudah bisa berjalan sesuai rencana. Fitur tambahan seperti grafik analisis dan asisten AI juga membantu melengkapi tampilan aplikasi.

Kekurangannya, data yang dipakai masih terbatas pada 224 baris untuk wilayah Sumatera (1993–2020) dan hanya melihat faktor luas panen serta iklim, belum memasukkan faktor lain seperti jenis bibit, pemupukan, atau hama. 

*(Catatan: Model dengan nilai R² paling mendekati 1 serta MAE dan RMSE paling rendah menunjukkan performa prediksi terbaik pada data uji.)*

## Cara menjalankan

### 1. Menjalankan aplikasi di Windows
Jalankan perintah berikut dari folder utama proyek:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install Django==6.1.3 pandas==3.1.1 numpy==2.5.5 scikit-learn==1.9.1 joblib==1.6.0 matplotlib==3.11.2 seaborn==0.13.2
python manage.py migrate
python manage.py runserver