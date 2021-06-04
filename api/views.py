from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import Favorite, Follow, Purchase
from .serializers import FavoriteSerializer

User = get_user_model()

UNKNOWN_ERROR = 'Произошла неизвестная ошибка'


class FavoriteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    lookup_field = 'recipe'
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'detail': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST, )
        if not Favorite.objects.filter(
                user=request.user,
                recipe=serializer.validated_data['recipe']).exists():
            serializer.save(user=request.user)
        return Response({'success': True}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance and not instance.delete():
            return Response(
                {'success': False, 'detail': UNKNOWN_ERROR},
                status=status.HTTP_400_BAD_REQUEST,)
        return Response({'success': True}, status=status.HTTP_200_OK)
