from django.urls import path

from .views import index, add_restaurant, restaurant_detail

urlpatterns = [
    path('', index, name='home'),
    path('add_restaurant/', add_restaurant, name='add_restaurant'),
    path('restaurant/<int:pk>/', restaurant_detail, name='restaurant-detail'),
]