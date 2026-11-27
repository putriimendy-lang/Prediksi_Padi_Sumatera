from django import forms


class PrediksiForm(forms.Form):
    provinsi = forms.ChoiceField(
        label='Provinsi',
        choices=[
            ('Aceh', 'Aceh'),
            ('Sumatera Utara', 'Sumatera Utara'),
            ('Sumatera Barat', 'Sumatera Barat'),
            ('Riau', 'Riau'),
            ('Jambi', 'Jambi'),
            ('Sumatera Selatan', 'Sumatera Selatan'),
            ('Bengkulu', 'Bengkulu'),
            ('Lampung', 'Lampung'),
        ],
    )
    tahun = forms.IntegerField(
        label='Tahun prediksi',
        min_value=1993,
        max_value=2100,
        initial=2025,
    )
    luas_panen = forms.FloatField(
        label='Luas panen (hektare)',
        min_value=0,
    )
    curah_hujan = forms.FloatField(
        label='Curah hujan',
        min_value=0,
    )
    kelembapan = forms.FloatField(
        label='Kelembapan (%)',
        min_value=0,
        max_value=100,
    )
    suhu_rata_rata = forms.FloatField(
        label='Suhu rata-rata (°C)',
        min_value=0,
    )
    model = forms.ChoiceField(
        label='Model prediksi',
        choices=[
            ('linear_regression', 'Linear Regression'),
            ('random_forest', 'Random Forest'),
        ],
    )


class AsistenChatForm(forms.Form):
    pesan = forms.CharField(
        label='Pesan',
        max_length=500,
        strip=True,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Tanyakan tentang data atau produksi padi...',
            'autocomplete': 'off',
            'class': 'chat-input',
        }),
    )
