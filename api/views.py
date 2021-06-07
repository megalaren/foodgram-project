from django.contrib.auth import get_user_model
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response

from .models import Favorite, Follow, Purchase
from recipes.models import Ingredient
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, PurchaseSerializer)

User = get_user_model()

UNKNOWN_ERROR = 'Произошла неизвестная ошибка'


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'detail': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST, )
        is_exists = self.get_queryset().filter(
            user=request.user,
            **{self.lookup_field: serializer.validated_data[self.lookup_field]}
        ).exists()
        if not is_exists:
            serializer.save(user=request.user)
        return Response({'success': True}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance and not instance.delete():
            return Response(
                {'success': False, 'detail': UNKNOWN_ERROR},
                status=status.HTTP_400_BAD_REQUEST,)
        return Response({'success': True}, status=status.HTTP_200_OK)


class IngredientViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^title',)


class FavoriteViewSet(CreateDestroyViewSet):
    lookup_field = 'recipe'
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class FollowViewSet(CreateDestroyViewSet):
    lookup_field = 'author'
    serializer_class = FollowSerializer

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)


class PurchaseViewSet(CreateDestroyViewSet):
    lookup_field = 'recipe'
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user)
