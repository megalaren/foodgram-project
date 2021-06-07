from rest_framework import serializers

from .models import Favorite, Follow, Purchase
from recipes.models import Ingredient


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', )


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('author', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('title', 'dimension')


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ('recipe', )
