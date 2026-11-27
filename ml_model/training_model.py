import pandas as pd
import numpy as np
import os
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Membaca dataset
data = pd.read_csv("dataset/Data_Tanaman_Padi_Sumatera.csv")

# Membagi data berdasarkan tahun
data_training = data[data["Tahun"] <= 2015]
data_testing = data[data["Tahun"] >= 2016]

# Menentukan variabel input dan target
fitur = [
    "Provinsi",
    "Tahun",
    "Luas Panen",
    "Curah hujan",
    "Kelembapan",
    "Suhu rata-rata",
]

X_train = data_training[fitur]
y_train = data_training["Produksi"]

X_test = data_testing[fitur]
y_test = data_testing["Produksi"]

# Menentukan kolom kategori dan numerik
kolom_kategori = ["Provinsi"]
kolom_numerik = [
    "Tahun",
    "Luas Panen",
    "Curah hujan",
    "Kelembapan",
    "Suhu rata-rata",
]

# Preprocessing data
preprocessing = ColumnTransformer(
    transformers=[
        ("kategori", OneHotEncoder(handle_unknown="ignore"), kolom_kategori),
        ("numerik", "passthrough", kolom_numerik),
    ]
)

# Menyiapkan algoritma
algoritma = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        random_state=42
    ),
}

# Membuat folder untuk model
os.makedirs("ml_model/saved_models", exist_ok=True)

hasil_evaluasi = []

# Training dan evaluasi setiap model
for nama, model in algoritma.items():

    # Menggabungkan preprocessing dan model
    pipeline = Pipeline([
        ("preprocessing", preprocessing),
        ("model", model),
    ])

    # Training model
    pipeline.fit(X_train, y_train)

    # Prediksi data testing
    prediksi = pipeline.predict(X_test)

    # Menghitung metrik evaluasi
    mae = mean_absolute_error(y_test, prediksi)
    rmse = np.sqrt(mean_squared_error(y_test, prediksi))
    r2 = r2_score(y_test, prediksi)

    # Menampilkan hasil
    print("\n" + "=" * 40)
    print("Model:", nama)
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("R2:", r2)

    # Menyimpan model
    nama_file = nama.lower().replace(" ", "_")
    joblib.dump(
        pipeline,
        f"ml_model/saved_models/{nama_file}.joblib"
    )

    # Menyimpan hasil evaluasi
    hasil_evaluasi.append({
        "Model": nama,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    })

# Menyimpan tabel evaluasi
hasil = pd.DataFrame(hasil_evaluasi)
hasil.to_csv("ml_model/hasil_evaluasi.csv", index=False)

print("\nHasil evaluasi berhasil disimpan.")