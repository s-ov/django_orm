from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from datetime import date

from django.db.models.functions import Lower
from django.db.models import Q

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.constraints import CheckConstraint

def validate_restaurant_name_tarts_with_a(value: Any) -> None:
    """Custom validator"""
    if not value.startswith('A'):
        raise ValidationError('Name must start with a')


class Restaurant(models.Model):
    class TypeChoices(models.TextChoices):
        INDIAN = 'IN', 'Indian'
        ITALIAN = 'IT', 'Italian'
        CHINESE = 'CH', 'Chinese'
        MEXICAN = 'MX', 'Mexican'
        GREEK = 'GR', 'Greek'
        FASTFOOD = 'FF', 'FastFood'
        OTHER = 'OT', 'Other'

    name = models.CharField(
        max_length=100, 
        validators=[validate_restaurant_name_tarts_with_a],
        unique=True)
    website = models.URLField(default='', null=True, blank=True)
    date_opened = models.DateField(null=True, blank=True)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)], null=True, blank=True)
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)], null=True, blank=True)
    restaurant_type = models.CharField(max_length=2, choices=TypeChoices.choices, default=None)
    capacity = models.PositiveSmallIntegerField(null=True, blank=True)
    nickname = models.CharField(max_length=100, default='')
    comments = GenericRelation('Comment', related_query_name='restaurant')

    @property
    def restaurant_name(self):
        return self.nickname or self.name
    
    @property
    def was_opened_this_year(self) -> bool:
        current_year = timezone.now().year
        return self.date_opened.year == current_year
    
    def is_opened_after(self, date: date) -> bool:
        return self.date_opened > date
    
    def get_absolute_url(self):
        return reverse("restaurant-detail", kwargs={"pk": self.pk})
    

    class Meta:
        ordering = [Lower('name')]
        get_latest_by = 'date_opened'
        constraints = [
            models.CheckConstraint(
                name='valid_latitude',
                check=Q(latitude__gte=-90, latitude__lte=90),
                violation_error_message='Invalid latitude: it must fall between -90 and 90'
            ),
            models.CheckConstraint(
                name='valid_longitude',
                check=Q(longitude__gte=-180, longitude__lte=180),
                violation_error_message='Invalid longitude: it must fall between -180 and 180'
            ),
            models.UniqueConstraint(
                Lower('name'),
                name='name_uniq_constraint'
            )
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)


class Staff(models.Model):
    name = models.CharField(max_length=128)
    restaurants = models.ManyToManyField(Restaurant, through='StaffRestaurant')

    def __str__(self) -> str:
        return self.name
    

class StaffRestaurant(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    salary = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return self.staff.name
    

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='ratings')
    rating = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comments = GenericRelation('Comment')

    def __str__(self) -> str:
        return f"Rating: {self.rating}"
    
    class Meta:
        """constraints - reserved word"""
        constraints = [
            models.CheckConstraint(
                name='rating_value_valid',
                check=Q(rating__gte=1, rating__lte=5),
                violation_error_message='Invalid rating: it must fall between 1 and 5'
            ),
            # 1 user 1 comment to certain restaurant
            models.UniqueConstraint(
                fields=['user', 'restaurant'],
                name='user_restaurant_uniq'
            ),
        ]
    

class Sale(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, related_name='sales')
    income = models.DecimalField(max_digits=8, decimal_places=2)
    expenditure = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    date_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"Sale: {self.income}"
    

class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveSmallIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
