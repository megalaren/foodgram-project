from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import Recipe, Tag

User = get_user_model()


def index(request):
    recipes = Recipe.objects.select_related('author')
    all_tags = Tag.objects.all()
    return render(request, 'recipes/index.html', {
        'recipes': recipes,
        'all_tags': all_tags,
    })


def recipe_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.select_related('author'),
        id=recipe_id,
    )
    ingredients = recipe.ingredients_count.annotate(
        title=F('ingredient__title'),
        unit=F('ingredient__unit')
    )
    return render(request, 'recipes/singlePage.html', {
        'recipe': recipe,
        'ingredients': ingredients,
    })
