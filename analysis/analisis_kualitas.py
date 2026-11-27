import pandas as pd

# Membaca dataset
data = pd.read_csv("dataset/Data_Tanaman_Padi_Sumatera.csv")

# Memeriksa data kosong
print("Jumlah Data Kosong:")
print(data.isnull().sum())

# Memeriksa data duplikat
print("\nJumlah Data Duplikat:")
print(data.duplicated().sum())

# Statistik deskriptif
print("\nStatistik Deskriptif:")
print(data.describe())

# Daftar provinsi
print("\nDaftar Provinsi:")
print(data["Provinsi"].unique())

# Rentang tahun
print("\nRentang Tahun:")
print(data["Tahun"].min(), "-", data["Tahun"].max())