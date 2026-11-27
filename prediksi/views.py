
import csv
from pathlib import Path

import joblib
import pandas as pd
from django.db import models
from django.shortcuts import redirect, render
from django.utils import timezone

from .chatbot import GeminiChatError, jawab_pertanyaan_ai, konteks_data_padi
from .forms import AsistenChatForm, PrediksiForm
from .models import DataPadi


def beranda(request):
    data = DataPadi.objects.all()
    data_awal = data.order_by('tahun').first()
    data_akhir = data.order_by('-tahun').first()

    context = {
        'jumlah_data': data.count(),
        'jumlah_provinsi': data.values('provinsi').distinct().count(),
        'tahun_awal': data_awal.tahun if data_awal else '-',
        'tahun_akhir': data_akhir.tahun if data_akhir else '-',
        'halaman_aktif': 'beranda',
    }

    return render(request, 'prediksi/beranda.html', context)


def halaman_dataset(request):
    data = DataPadi.objects.all()

    context = {
        'data_padi': data,
        'jumlah_data': data.count(),
        'halaman_aktif': 'dataset',
    }

    return render(request, 'prediksi/dataset.html', context)


def halaman_analisis(request):
    data = DataPadi.objects.all()

    produksi_provinsi = list(
        data.values('provinsi')
        .annotate(total_produksi=models.Sum('produksi'))
        .order_by('-total_produksi')
    )

    produksi_tahun = list(
        data.values('tahun')
        .annotate(total_produksi=models.Sum('produksi'))
        .order_by('tahun')
    )

    context = {
        'produksi_provinsi': produksi_provinsi,
        'produksi_tahun': produksi_tahun,
        'halaman_aktif': 'analisis',
    }

    return render(request, 'prediksi/analisis.html', context)


def halaman_prediksi(request):
    nama_sesi = 'riwayat_prediksi'
    hasil_sesi = 'hasil_prediksi_terakhir'

    if request.method == 'POST' and request.POST.get('aksi') == 'hapus_riwayat':
        request.session.pop(nama_sesi, None)
        request.session.pop(hasil_sesi, None)
        return redirect('prediksi')

    form = PrediksiForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        fitur = pd.DataFrame([{
            'Provinsi': data['provinsi'],
            'Tahun': data['tahun'],
            'Luas Panen': data['luas_panen'],
            'Curah hujan': data['curah_hujan'],
            'Kelembapan': data['kelembapan'],
            'Suhu rata-rata': data['suhu_rata_rata'],
        }])
        file_model = (
            Path(__file__).resolve().parent.parent
            / 'ml_model'
            / 'saved_models'
            / f"{data['model']}.joblib"
        )
        model = joblib.load(file_model)
        hasil_prediksi = float(model.predict(fitur)[0])
        nama_model = dict(form.fields['model'].choices)[data['model']]
        riwayat = request.session.get(nama_sesi, [])
        riwayat.insert(0, {
            'waktu': timezone.localtime().strftime('%Y-%m-%d %H:%M %Z'),
            'provinsi': data['provinsi'],
            'tahun': data['tahun'],
            'luas_panen': data['luas_panen'],
            'curah_hujan': data['curah_hujan'],
            'kelembapan': data['kelembapan'],
            'suhu_rata_rata': data['suhu_rata_rata'],
            'model': nama_model,
            'hasil': hasil_prediksi,
        })
        request.session[nama_sesi] = riwayat[:20]
        request.session[hasil_sesi] = {
            'nilai': hasil_prediksi,
            'model': nama_model,
        }
        return redirect('prediksi')

    hasil_terakhir = request.session.pop(hasil_sesi, None)

    return render(request, 'prediksi/prediksi.html', {
        'form': form,
        'hasil_terakhir': hasil_terakhir,
        'riwayat_prediksi': request.session.get(nama_sesi, []),
        'halaman_aktif': 'prediksi',
    })


def halaman_evaluasi(request):
    file_evaluasi = Path(__file__).resolve().parent.parent / 'ml_model' / 'hasil_evaluasi.csv'
    with file_evaluasi.open(encoding='utf-8', newline='') as berkas:
        hasil_evaluasi = list(csv.DictReader(berkas))

    return render(request, 'prediksi/evaluasi.html', {
        'hasil_evaluasi': hasil_evaluasi,
        'halaman_aktif': 'evaluasi',
    })


def halaman_asisten(request):
    nama_sesi = 'asisten_riwayat'
    if request.method == 'POST' and request.POST.get('aksi') == 'hapus':
        request.session.pop(nama_sesi, None)
        return redirect('asisten')

    riwayat = request.session.get(nama_sesi, [])
    form = AsistenChatForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        pesan = form.cleaned_data['pesan']
        try:
            konteks = konteks_data_padi(pesan)
            jawaban = jawab_pertanyaan_ai(pesan, riwayat.copy(), konteks)
        except GeminiChatError as error:
            form.add_error(None, str(error))
        else:
            riwayat.extend([
                {'peran': 'pengguna', 'teks': pesan},
                {'peran': 'asisten', 'teks': jawaban},
            ])
            request.session[nama_sesi] = riwayat[-30:]
            return redirect('asisten')

    return render(request, 'prediksi/asisten.html', {
        'form': form,
        'riwayat': riwayat,
        'halaman_aktif': 'asisten',
    })


def halaman_tentang(request):
    ringkasan_data = DataPadi.objects.aggregate(
        jumlah_data=models.Count('pk'),
        jumlah_provinsi=models.Count('provinsi', distinct=True),
        tahun_awal=models.Min('tahun'),
        tahun_akhir=models.Max('tahun'),
    )
    return render(request, 'prediksi/tentang.html', {
        **ringkasan_data,
        'halaman_aktif': 'tentang',
    })
