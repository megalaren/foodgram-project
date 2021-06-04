from rest_framework import serializers

from .models import Favorite, Follow, Purchase


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', )
