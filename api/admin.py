from django.contrib import admin

from .models import Favorite, Follow, Purchase


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    ordering = ['user']


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'user')
    ordering = ['author']


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    ordering = ['user']


admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Purchase, PurchaseAdmin)
