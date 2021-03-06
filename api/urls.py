from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                    PurchaseViewSet)

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'subscriptions', FollowViewSet, basename='subscriptions')
router.register(r'purchases', PurchaseViewSet, basename='purchases')

urlpatterns = [
    path('v1/', include(router.urls)),
]
