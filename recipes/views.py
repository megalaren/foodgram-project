from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, F, OuterRef
from django.shortcuts import get_object_or_404, render

from .models import Recipe, Tag
from api.models import Favorite, Follow, Purchase

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


@login_required
def follow_index(request):
    authors = User.objects.filter(
        following__user=request.user).prefetch_related('recipes').annotate(
        recipes_count=Count('recipes'))
    purchases_count = request.user.purchases.count()
    all_tags = Tag.objects.all()

    return render(request, 'recipes/myFollow.html', {
        'authors': authors,
        'all_tags': all_tags,
        'purchases_count': purchases_count
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    user = request.user
    is_follow = False
    purchases_count = 0
    if user.is_authenticated:
        purchases_count = user.purchases.count()
        favorites_recipes = Favorite.objects.filter(user=user,
            recipe=OuterRef('pk'))
        purchases_recipes = Purchase.objects.filter(user=request.user,
            recipe=OuterRef('pk'))
        recipes = recipes.annotate(
            is_favorite=Exists(favorites_recipes)).annotate(
            is_purchase=Exists(purchases_recipes))
        is_follow = Follow.objects.filter(user=user, author=author).exists()

    all_tags = Tag.objects.all()

    return render(request, 'recipes/authorRecipe.html', {
        'all_tags': all_tags,
        'author': author,
        'is_follow': is_follow,
        'purchases_count': purchases_count,
        'recipes': recipes,
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
