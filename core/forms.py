from django import forms
from .models import Rating, Restaurant, Sale

# from django.core.validators import MinValueValidator, MaxValueValidator
# class RatingForm(forms.Form):
#     rating = forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['restaurant', 'user', 'rating']


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'date_opened', 'latitude', 'longitude', 'restaurant_type']
