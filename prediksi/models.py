from django.db import models


class DataPadi(models.Model):
    provinsi = models.CharField(max_length=100)
    tahun = models.IntegerField()
    produksi = models.FloatField()
    luas_panen = models.FloatField()
    curah_hujan = models.FloatField()
    kelembapan = models.FloatField()
    suhu_rata_rata = models.FloatField()

    class Meta:
        db_table = 'data_padi'
        ordering = ['provinsi', 'tahun']

    def __str__(self):
        return f"{self.provinsi} - {self.tahun}"