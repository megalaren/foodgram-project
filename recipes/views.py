from django.contrib.auth import get_user_model
from django.db.models import Exists, F, OuterRef
from django.shortcuts import get_object_or_404, render

from .models import Recipe, Tag
from api.models import Favorite, Purchase

User = get_user_model()


def index(request):
    recipes = Recipe.objects.select_related('author')
    user = request.user
    purchases_count = 0
    if user.is_authenticated:
        purchases_count = user.purchases.count()
        favorites_recipes = Favorite.objects.filter(
            user=user,
            recipe=OuterRef('pk')
        )
        purchases_recipes = Purchase.objects.filter(
            user=request.user,
            recipe=OuterRef('pk')
        )
        recipes = recipes.annotate(
            is_favorite=Exists(favorites_recipes)).annotate(
            is_purchase=Exists(purchases_recipes))

    all_tags = Tag.objects.all()

    return render(request, 'recipes/index.html', {
        'recipes': recipes,
        'all_tags': all_tags,
        'purchases_count': purchases_count
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
