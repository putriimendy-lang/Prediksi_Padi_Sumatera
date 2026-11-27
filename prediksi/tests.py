import json
from unittest.mock import patch

from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .chatbot import GeminiChatError, jawab_pertanyaan_ai
from .models import DataPadi


class MenuPageTests(TestCase):
    def test_all_menu_pages_load(self):
        menu_names = [
            'beranda',
            'dataset',
            'analisis',
            'prediksi',
            'evaluasi',
            'asisten',
            'tentang',
        ]

        for menu_name in menu_names:
            with self.subTest(menu=menu_name):
                response = self.client.get(reverse(menu_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="active"')
                for destination in menu_names:
                    self.assertContains(response, f'href="{reverse(destination)}"')
                self.assertContains(response, f'href="{reverse("admin:index")}"')
                self.assertNotContains(response, 'href="#"')

    def test_admin_requires_login_and_registers_rice_data(self):
        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('admin:login')))
        self.assertEqual(
            self.client.get(reverse('admin:login')).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('admin:prediksi_datapadi_changelist')).status_code,
            302,
        )

    def test_admin_has_data_change_history(self):
        admin_user = get_user_model().objects.create_superuser(
            username='history-admin',
            email='history@example.com',
            password=None,
        )
        data_padi = DataPadi.objects.create(
            provinsi='Aceh',
            tahun=2020,
            produksi=123.5,
            luas_panen=100,
            curah_hujan=150,
            kelembapan=80,
            suhu_rata_rata=27,
        )
        LogEntry.objects.create(
            action_time=timezone.now(),
            user=admin_user,
            content_type=ContentType.objects.get_for_model(DataPadi),
            object_id=str(data_padi.pk),
            object_repr=str(data_padi),
            action_flag=ADDITION,
            change_message='Added through admin.',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:prediksi_datapadi_history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Riwayat Input Data Padi')
        self.assertContains(response, 'history-admin')
        self.assertContains(response, 'Aceh - 2020')
        self.assertContains(
            self.client.get(reverse('admin:prediksi_datapadi_changelist')),
            reverse('admin:prediksi_datapadi_history'),
        )

    def test_about_page_explains_django_and_shows_dataset_summary(self):
        DataPadi.objects.create(
            provinsi='Aceh',
            tahun=2018,
            produksi=123.5,
            luas_panen=100,
            curah_hujan=150,
            kelembapan=80,
            suhu_rata_rata=27,
        )
        DataPadi.objects.create(
            provinsi='Aceh',
            tahun=2019,
            produksi=130,
            luas_panen=105,
            curah_hujan=155,
            kelembapan=82,
            suhu_rata_rata=27.5,
        )

        response = self.client.get(reverse('tentang'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django di dalam aplikasi')
        self.assertContains(response, 'Django Admin')
        self.assertContains(response, '<strong>2</strong>')
        self.assertContains(response, '2018–2019')

    def test_prediction_form_returns_model_result(self):
        response = self.client.post(
            reverse('prediksi'),
            {
                'provinsi': 'Aceh',
                'tahun': 2025,
                'luas_panen': 100000,
                'curah_hujan': 200,
                'kelembapan': 80,
                'suhu_rata_rata': 27,
                'model': 'linear_regression',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hasil Prediksi')
        self.assertContains(response, 'Linear Regression')
        self.assertContains(response, 'Riwayat Prediksi')
        self.assertContains(response, 'Aceh')
        self.assertEqual(len(self.client.session['riwayat_prediksi']), 1)

    def test_prediction_history_can_be_cleared(self):
        session = self.client.session
        session['riwayat_prediksi'] = [{'provinsi': 'Aceh'}]
        session.save()

        response = self.client.post(
            reverse('prediksi'),
            {'aksi': 'hapus_riwayat'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('riwayat_prediksi', self.client.session)
        self.assertContains(response, 'Belum ada riwayat prediksi di sesi ini.')

    def test_prediction_form_rejects_invalid_values(self):
        response = self.client.post(reverse('prediksi'), {
            'provinsi': 'Aceh',
            'tahun': 2025,
            'luas_panen': 100000,
            'curah_hujan': 200,
            'kelembapan': 120,
            'suhu_rata_rata': 27,
            'model': 'linear_regression',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ensure this value is less than or equal to 100.')
        self.assertNotContains(response, 'Hasil Prediksi')

    def test_assistant_uses_gemini_response_and_keeps_conversation(self):
        with patch(
            'prediksi.views.jawab_pertanyaan_ai',
            return_value='Halo, ada yang bisa saya bantu?',
        ) as jawab:
            response = self.client.post(
                reverse('asisten'),
                {'pesan': 'Halo'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Halo, ada yang bisa saya bantu?')
        self.assertEqual(
            self.client.session['asisten_riwayat'],
            [
                {'peran': 'pengguna', 'teks': 'Halo'},
                {
                    'peran': 'asisten',
                    'teks': 'Halo, ada yang bisa saya bantu?',
                },
            ],
        )
        jawab.assert_called_once_with(
            'Halo',
            [],
            'Dataset PadiPredict belum berisi data.',
        )

    def test_assistant_passes_matching_dataset_facts_to_gemini(self):
        DataPadi.objects.create(
            provinsi='Aceh',
            tahun=2020,
            produksi=12.5,
            luas_panen=100,
            curah_hujan=150,
            kelembapan=80,
            suhu_rata_rata=27,
        )

        with patch(
            'prediksi.views.jawab_pertanyaan_ai',
            return_value='Produksi Aceh tahun 2020 tercatat 12,5.',
        ) as jawab:
            response = self.client.post(
                reverse('asisten'),
                {'pesan': 'Produksi Aceh tahun 2020?'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produksi Aceh tahun 2020 tercatat 12,5.')
        self.assertIn(
            'Total produksi Aceh pada 2020: 12,5 (1 baris).',
            jawab.call_args.args[2],
        )

    def test_assistant_passes_model_evaluation_to_gemini(self):
        with patch(
            'prediksi.views.jawab_pertanyaan_ai',
            return_value='Linear Regression memiliki RMSE terendah.',
        ) as jawab:
            response = self.client.post(
                reverse('asisten'),
                {'pesan': 'Model dengan RMSE terendah?'},
                follow=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Linear Regression', jawab.call_args.args[2])
        self.assertIn('RMSE', jawab.call_args.args[2])

    def test_gemini_request_includes_conversation_history(self):
        response_body = {
            'steps': [{
                'type': 'model_output',
                'content': [{
                    'type': 'text',
                    'text': 'Gemini menjawab.',
                }],
            }],
        }
        with (
            patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}),
            patch('prediksi.chatbot.urlopen') as urlopen,
        ):
            urlopen.return_value.__enter__.return_value.read.return_value = (
                json.dumps(response_body).encode('utf-8')
            )
            jawaban = jawab_pertanyaan_ai(
                'Pertanyaan baru',
                [{'peran': 'pengguna', 'teks': 'Pertanyaan sebelumnya'}],
            )

        permintaan = urlopen.call_args.args[0]
        isi_permintaan = json.loads(permintaan.data.decode('utf-8'))
        self.assertEqual(jawaban, 'Gemini menjawab.')
        self.assertIn('Pengguna: Pertanyaan sebelumnya', isi_permintaan['input'])
        self.assertIn('Pengguna: Pertanyaan baru', isi_permintaan['input'])
        self.assertEqual(
            permintaan.get_header('X-goog-api-key'),
            'test-key',
        )

    def test_gemini_requires_environment_api_key(self):
        with patch.dict('os.environ', {'GEMINI_API_KEY': ''}):
            with self.assertRaisesRegex(GeminiChatError, 'GEMINI_API_KEY'):
                jawab_pertanyaan_ai('Halo', [])

    def test_assistant_shows_gemini_setup_error_without_saving_message(self):
        with patch(
            'prediksi.views.jawab_pertanyaan_ai',
            side_effect=GeminiChatError(
                'Kunci Gemini belum disiapkan. Atur variabel lingkungan GEMINI_API_KEY.'
            ),
        ):
            response = self.client.post(
                reverse('asisten'),
                {'pesan': 'Halo'},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GEMINI_API_KEY')
        self.assertNotIn('asisten_riwayat', self.client.session)

    def test_assistant_rejects_empty_message(self):
        response = self.client.post(reverse('asisten'), {'pesan': '   '})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_assistant_shows_clickable_question_suggestions(self):
        response = self.client.get(reverse('asisten'))

        self.assertContains(response, 'data-chat-prompt="Produksi Aceh tahun 2020?"')
        self.assertContains(response, 'data-chat-prompt="Bagaimana cara membuat prediksi?"')
        self.assertContains(response, 'data-chat-prompt="Model dengan RMSE terendah?"')

    def test_assistant_can_clear_conversation(self):
        with patch(
            'prediksi.views.jawab_pertanyaan_ai',
            return_value='Halo',
        ):
            self.client.post(
                reverse('asisten'),
                {'pesan': 'Halo'},
                follow=True,
            )
        response = self.client.post(
            reverse('asisten'),
            {'aksi': 'hapus'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('asisten_riwayat', self.client.session)
        self.assertNotContains(response, 'Hapus percakapan')
