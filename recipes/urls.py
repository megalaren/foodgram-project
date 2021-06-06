from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('subscriptions/',
         views.follow_index,
         name='follow_index'),
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
    path('recipe/<int:recipe_id>/',
         views.recipe_view,
         name='recipe'),
]
