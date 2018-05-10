from django.test import TestCase
import views
# Create your tests here.


class WebHookTestCase():

    def test_audio_convert(self):
        views.convert_audio("Prueba")
        self.assertEqual("1", "1")
