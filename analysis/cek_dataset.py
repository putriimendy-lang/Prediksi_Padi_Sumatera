import pandas as pd

# Membaca dataset padi
data = pd.read_csv("dataset/Data_Tanaman_Padi_Sumatera.csv")

# Menampilkan 5 data pertama
print("5 Data Pertama:")
print(data.head())

# Menampilkan informasi dataset
print("\nInformasi Dataset:")
print(data.info())

# Menampilkan ukuran dataset
print("\nUkuran Dataset:")
print(data.shape)