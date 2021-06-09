from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('favorite/',
         views.favorite,
         name='favorite'),
    path('new_recipe/',
         views.new_recipe,
         name='new_recipe'),
    path('subscriptions/',
         views.follow_index,
         name='follow_index'),
    path('profile/<str:username>/',
         views.profile,
         name='profile'),
    path('recipe/<int:recipe_id>/',
         views.recipe_view,
         name='recipe'),
    path('recipe_edit/<int:recipe_id>/',
         views.recipe_edit,
         name='recipe_edit'),
    path('recipe_delete/<int:recipe_id>/',
         views.recipe_delete,
         name='recipe_delete'),
]
