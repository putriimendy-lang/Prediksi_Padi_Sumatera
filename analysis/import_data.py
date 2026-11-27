import os
import sys
import pandas as pd
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from prediksi.models import DataPadi

lokasi_dataset = BASE_DIR / 'dataset' / 'Data_Tanaman_Padi_Sumatera.csv'

data = pd.read_csv(lokasi_dataset)

DataPadi.objects.all().delete()

data_padi = [
    DataPadi(
        provinsi=row['Provinsi'],
        tahun=int(row['Tahun']),
        produksi=float(row['Produksi']),
        luas_panen=float(row['Luas Panen']),
        curah_hujan=float(row['Curah hujan']),
        kelembapan=float(row['Kelembapan']),
        suhu_rata_rata=float(row['Suhu rata-rata'])
    )
    for _, row in data.iterrows()
]

DataPadi.objects.bulk_create(data_padi)

print(f"Berhasil memasukkan {DataPadi.objects.count()} data ke database SQLite.")