import pandas as pd

# Membaca dataset
data = pd.read_csv("dataset/Data_Tanaman_Padi_Sumatera.csv")

# Menentukan variabel input (X) dan target (Y)
X = data[
    [
        "Provinsi",
        "Tahun",
        "Luas Panen",
        "Curah hujan",
        "Kelembapan",
        "Suhu rata-rata",
    ]
]

y = data["Produksi"]

# Membagi data berdasarkan tahun
data_training = data[data["Tahun"] <= 2015]
data_testing = data[data["Tahun"] >= 2016]

# Memisahkan X dan Y pada data training
X_train = data_training[
    [
        "Provinsi",
        "Tahun",
        "Luas Panen",
        "Curah hujan",
        "Kelembapan",
        "Suhu rata-rata",
    ]
]
y_train = data_training["Produksi"]

# Memisahkan X dan Y pada data testing
X_test = data_testing[
    [
        "Provinsi",
        "Tahun",
        "Luas Panen",
        "Curah hujan",
        "Kelembapan",
        "Suhu rata-rata",
    ]
]
y_test = data_testing["Produksi"]

# Menampilkan hasil pembagian data
print("Jumlah Data Keseluruhan:", len(data))
print("Jumlah Data Training:", len(X_train))
print("Jumlah Data Testing:", len(X_test))

print("\nRentang Tahun Training:")
print(data_training["Tahun"].min(), "-", data_training["Tahun"].max())

print("\nRentang Tahun Testing:")
print(data_testing["Tahun"].min(), "-", data_testing["Tahun"].max())

print("\nJumlah Data Training per Provinsi:")
print(data_training["Provinsi"].value_counts().sort_index())

print("\nJumlah Data Testing per Provinsi:")
print(data_testing["Provinsi"].value_counts().sort_index())

print("\nNama Variabel Input:")
print(X_train.columns.tolist())

print("\nNama Variabel Target:")
print(y_train.name)