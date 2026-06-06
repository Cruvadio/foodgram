from django.contrib import admin
from django.contrib.admin import ModelAdmin, register

from .models import Ingredient, Recipe, Tag


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('id', 'name', 'slug')


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    fields = (
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'tags',
        'favourites_count',
    )
    readonly_fields = ['favourites_count']
    inlines = (IngredientInline,)
    search_fields = ('name', 'author__first_name', 'author__last_name')
    list_filter = ('author', 'tags')

    @admin.display(description='Количество лайков')
    def favourites_count(self, obj):
        return obj.favourited_by.count()


# Register your models here.
