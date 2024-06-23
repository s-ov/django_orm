from django.test import TestCase
from django.utils import timezone
from .models import Restaurant


class RestaurantTestCase(TestCase):
    def test_restaurant_name_property(self):
        restaurant = Restaurant(name='test')
        self.assertEqual(restaurant.restaurant_name, 'test')

        restaurant.nickname = 'busty'
        self.assertEqual(restaurant.restaurant_name, 'busty')


    def test_was_opened_this_year(self):
        restaurant = Restaurant(date_opened=timezone.now().date())
        self.assertEqual(restaurant.was_opened_this_year, True)
