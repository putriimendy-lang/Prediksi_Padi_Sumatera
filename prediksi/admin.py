from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path

from .models import DataPadi


@admin.register(DataPadi)
class DataPadiAdmin(admin.ModelAdmin):
    change_list_template = 'admin/prediksi/datapadi/change_list.html'
    list_display = (
        'provinsi',
        'tahun',
        'produksi',
        'luas_panen',
        'curah_hujan',
        'kelembapan',
        'suhu_rata_rata',
    )
    list_filter = ('provinsi', 'tahun')
    search_fields = ('provinsi',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'riwayat/',
                self.admin_site.admin_view(self.riwayat_view),
                name='prediksi_datapadi_history',
            ),
        ]
        return custom_urls + urls

    def riwayat_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        content_type = ContentType.objects.get_for_model(self.model)
        riwayat = (
            LogEntry.objects
            .filter(content_type=content_type)
            .select_related('user')
            .order_by('-action_time')
        )
        halaman = Paginator(riwayat, 50).get_page(request.GET.get('page'))
        context = {
            **self.admin_site.each_context(request),
            'title': 'Riwayat Input Data Padi',
            'opts': self.model._meta,
            'page_obj': halaman,
        }
        return TemplateResponse(
            request,
            'admin/prediksi/datapadi/riwayat.html',
            context,
        )
