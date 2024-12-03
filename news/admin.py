from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_created')
    fields = ['title_uz', 'title_ru', 'title_en', 'body_uz', 'body_ru', 'body_en', 'image']

