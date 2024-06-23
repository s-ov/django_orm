from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Restaurant, Rating, Sale, Comment


class CommentInline(GenericTabularInline):
    model = Comment
    max_num = 1             # max number of related instances


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    inlines = [CommentInline]


class RatingAdmin(admin.ModelAdmin):
    list_display = ["id", "rating"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'content_type', 'object_id', 'content_object']


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Sale)
admin.site.register(Comment, CommentAdmin)
