from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.db.models import Count, F
from django.shortcuts import get_object_or_404, render, redirect

from .forms import RecipeForm
from .models import Recipe, Tag
from .utils import (get_ingredients_from_recipe, get_ingredients_from_request,
                    get_tags_from_request, get_recipes_for_index,
                    save_ingredients_and_tags)
from api.models import Favorite, Follow, Purchase

User = get_user_model()


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


@login_required
def new_recipe(request):
    all_tags = Tag.objects.all()
    if request.method != 'POST':
        return render(request, 'recipes/formRecipe.html', {
            'form': RecipeForm(),
            'all_tags': all_tags,
            'new_recipe': True,
        })
    form = RecipeForm(request.POST or None, files=request.FILES or None, )
    recipe_tags = get_tags_from_request(request, all_tags)
    ingredients, form = get_ingredients_from_request(request, form)

    if not form.is_valid():
        return render(request, 'recipes/formRecipe.html', {
            'all_tags': all_tags,
            'form': form,
            'ingredients': ingredients,
            'recipe_tags': recipe_tags,
            'new_recipe': True,
        })
    # если валидна, то сохраняем рецепт и добавляем в него тэги и ингредиенты
    recipe = form.save(commit=False)
    recipe.author = request.user
    recipe.save()
    save_ingredients_and_tags(recipe, ingredients, recipe_tags)
    return redirect('recipe', recipe.id)


@login_required()
def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        return redirect('recipe', recipe_id)

    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe
    )
    all_tags = Tag.objects.all()
    if request.method != 'POST':
        ingredients = get_ingredients_from_recipe(recipe)
        recipe_tags = recipe.tags.all()
        return render(request, 'recipes/formRecipe.html', {
            'all_tags': all_tags,
            'form': form,
            'ingredients': ingredients,
            'recipe_tags': recipe_tags,
            'recipe_id': recipe_id,
        })

    recipe_tags = get_tags_from_request(request, all_tags)
    ingredients, form = get_ingredients_from_request(request, form)

    if not form.is_valid():
        return render(request, 'recipes/formRecipe.html', {
            'all_tags': all_tags,
            'form': form,
            'ingredients': ingredients,
            'recipe_tags': recipe_tags,
            'recipe_id': recipe_id,
        })
    # если валидна, то сохраняем рецепт и добавляем в него тэги и ингредиенты
    recipe = form.save(commit=False)
    recipe.save()
    save_ingredients_and_tags(recipe, ingredients, recipe_tags)
    return redirect('recipe', recipe.id)


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe', recipe_id)
    all_tags = Tag.objects.all()
    title = recipe.title
    recipe.delete()
    return render(request, 'recipes/recipe_delete_done.html', {
        'all_tags': all_tags,
        'title': title,
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
        dimension=F('ingredient__dimension')
    )
    return render(request, 'recipes/singlePage.html', {
        'author': author,
        'recipe': recipe,
        'ingredients': ingredients,
        'is_favorite': is_favorite,
        'is_follow': is_follow,
        'is_purchase': is_purchase,
    })
