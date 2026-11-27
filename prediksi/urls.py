
from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('dataset/', views.halaman_dataset, name='dataset'),
    path('analisis/', views.halaman_analisis, name='analisis'),
    path('prediksi/', views.halaman_prediksi, name='prediksi'),
    path('evaluasi/', views.halaman_evaluasi, name='evaluasi'),
    path('asisten-ai/', views.halaman_asisten, name='asisten'),
    path('tentang/', views.halaman_tentang, name='tentang'),
]
