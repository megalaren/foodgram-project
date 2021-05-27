from django.contrib.auth import get_user_model
from django.shortcuts import render

from .models import Recipe


User = get_user_model()


def index(request):
    recipes = Recipe.objects.select_related('author')
    return render(request, 'recipes/index.html', {
        'recipes': recipes,
    })
