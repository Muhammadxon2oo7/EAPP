from django.contrib import admin
from django import forms
from django.contrib.admin import ModelAdmin

from .models import (
    MainData, InformativeData, FinancialData, ObjectPhoto, Status, AllData,
    InvestorInfo, Category, Area, SmartNote, Currency, CurrencyPrice, Faq, CadastralPhoto, ProductPhoto, Image, Video
)


class AllDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_created', 'status')
    ordering = ('-date_created',)


class AllDataReady(AllData):
    class Meta:
        proxy = True


class AllDataReadyAdmin(AllDataAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(status=Status.CHECKING)


admin.site.register(AllData, AllDataAdmin)
admin.site.register(AllDataReady, AllDataReadyAdmin)


@admin.register(InformativeData)
class InformativeDataAdmin(ModelAdmin):
    list_display = ("product_info", "project_capacity", "user")
    ordering = ("-id",)


@admin.register(Category)
class CategoryDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'category',)
    fields = ['category_uz', 'category_ru', 'category_en',]


@admin.register(Area)
class AreaDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'location',)
    fields = ['location_uz', 'location_ru', 'location_en', 'lat', 'long',]


admin.site.register(MainData)
admin.site.register(FinancialData)
admin.site.register(ObjectPhoto)
admin.site.register(InvestorInfo)

# admin.site.register(SmartNote)
admin.site.register(CadastralPhoto)

admin.site.register(Currency)
admin.site.register(ProductPhoto)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


admin.site.register(CurrencyPrice)


class CurrencyPriceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'cb_price')
    ordering = ('-date',)


admin.site.register(Faq)


@admin.register(SmartNote)
class SmartNoteAdmin(ModelAdmin):
    list_display = ('id',)
    ordering = ("-id",)


admin.site.register(Image)
admin.site.register(Video)
