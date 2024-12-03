from modeltranslation.translator import TranslationOptions, register

from data.models import Category, Area

from news.models import News


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('category',)


@register(Area)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('location',)


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'body')