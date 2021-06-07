from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, F, OuterRef
from django.shortcuts import get_object_or_404, render

from .models import Recipe, Tag
from api.models import Favorite, Follow, Purchase

User = get_user_model()


def get_recipes_for_index(recipes, user):
    """Возвращает рецепты с полями is_favorite и is_purchase."""
    favorites_recipes = Favorite.objects.filter(
        user=user,
        recipe=OuterRef('pk')
    )
    purchases_recipes = Purchase.objects.filter(
        user=user,
        recipe=OuterRef('pk')
    )
    recipes = recipes.annotate(
        is_favorite=Exists(favorites_recipes)).annotate(
        is_purchase=Exists(purchases_recipes)
    )
    return recipes


def index(request):
    recipes = Recipe.objects.select_related('author')
    user = request.user
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)
    all_tags = Tag.objects.all()

    return render(request, 'recipes/index.html', {
        'recipes': recipes,
        'all_tags': all_tags,
    })


@login_required
def favorite(request):
    user = request.user
    recipes = Recipe.objects.filter(
        favorites__user=user).select_related('author')
    recipes = get_recipes_for_index(recipes, user)
    all_tags = Tag.objects.all()

    return render(request, 'recipes/favorite.html', {
        'recipes': recipes,
        'all_tags': all_tags,
    })


@login_required
def follow_index(request):
    authors = User.objects.filter(
        following__user=request.user).prefetch_related('recipes').annotate(
        recipes_count=Count('recipes'))
    all_tags = Tag.objects.all()

    return render(request, 'recipes/myFollow.html', {
        'authors': authors,
        'all_tags': all_tags,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    user = request.user
    is_follow = False
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)
        is_follow = Follow.objects.filter(user=user, author=author).exists()
    all_tags = Tag.objects.all()

    return render(request, 'recipes/authorRecipe.html', {
        'all_tags': all_tags,
        'author': author,
        'is_follow': is_follow,
        'recipes': recipes,
    })


def recipe_view(request, recipe_id):
    user = request.user
    recipe = get_object_or_404(
        Recipe,
        id=recipe_id,
    )
    author = recipe.author
    is_favorite = is_follow = is_purchase = False
    if user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=user, recipe=recipe).exists()
        is_follow = Follow.objects.filter(
            user=user, author=author).exists()
        is_purchase = Purchase.objects.filter(
            user=user, recipe=recipe).exists()

    ingredients = recipe.ingredients_count.annotate(
        title=F('ingredient__title'),
        unit=F('ingredient__unit')
    )
    return render(request, 'recipes/singlePage.html', {
        'author': author,
        'recipe': recipe,
        'ingredients': ingredients,
        'is_favorite': is_favorite,
        'is_follow': is_follow,
        'is_purchase': is_purchase,
    })
