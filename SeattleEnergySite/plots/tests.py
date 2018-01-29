from django.test import TestCase

# Create your tests here.
from .models import Building

class TestAllCombinations(TestCase):

    def setUp(self):
        import data

    def test_all(self):
        uses = Building.objects.values_list('main_use',flat=True).distinct()
        plot_types = [f.name for f in Building._meta.get_fields() 
                      if f.get_internal_type() is not 'CharField']

        for use in uses:
            for pt in plot_types:
                print(use,pt)
                response = self.client.post('/plots/',{'building_use':use,
                                                       'property':pt})

                self.assertEqual(response.status_code, 200)
