import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Membaca dataset
data = pd.read_csv("dataset/Data_Tanaman_Padi_Sumatera.csv")

# Membuat folder untuk menyimpan grafik
os.makedirs("analysis/hasil_visualisasi", exist_ok=True)

# 1. Grafik produksi padi berdasarkan tahun
produksi_tahun = data.groupby("Tahun")["Produksi"].sum()

plt.figure(figsize=(10, 5))
produksi_tahun.plot(kind="line", marker="o")
plt.title("Produksi Padi di Sumatera Berdasarkan Tahun")
plt.xlabel("Tahun")
plt.ylabel("Total Produksi")
plt.grid(True)
plt.tight_layout()
plt.savefig("analysis/hasil_visualisasi/produksi_tahun.png")
plt.show()

# 2. Grafik hubungan luas panen dan produksi
plt.figure(figsize=(8, 5))
sns.scatterplot(data=data, x="Luas Panen", y="Produksi")
plt.title("Hubungan Luas Panen dengan Produksi Padi")
plt.xlabel("Luas Panen")
plt.ylabel("Produksi")
plt.tight_layout()
plt.savefig("analysis/hasil_visualisasi/luas_produksi.png")
plt.show()

# 3. Heatmap korelasi
kolom_numerik = data.select_dtypes(include="number")
korelasi = kolom_numerik.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(korelasi, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Heatmap Korelasi Antarvariabel")
plt.tight_layout()
plt.savefig("analysis/hasil_visualisasi/heatmap_korelasi.png")
plt.show()

print("Seluruh visualisasi berhasil dibuat dan disimpan.")