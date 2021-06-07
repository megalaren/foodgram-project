from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Tag, Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    ordering = ['name']


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'dimension')
    ordering = ['title']


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'title', 'description', 'pub_date',
                    'image', 'cooking_time', 'get_tags')
    ordering = ['-pub_date']


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'quantity', 'dimension')
    ordering = ['pk']


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
