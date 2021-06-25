from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from api.models import Favorite, Follow, Purchase

from .forms import RecipeForm
from .models import Recipe, RecipeIngredient
from .utils import (get_ingredients_from_recipe, get_ingredients_from_request,
                    get_recipes_for_index, get_shop_list_pdf_binary,
                    get_tag_filtered_recipes, get_tags_from_request,
                    save_ingredients_and_tags)

User = get_user_model()

PER_PAGE = 6


def index(request):
    recipes = Recipe.objects.select_related('author')
    recipes, active_tags = get_tag_filtered_recipes(request, recipes)
    user = request.user
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/index.html', {
        'page': page,
        'paginator': paginator,
        'active_tags': active_tags,
    })


@login_required
def favorite(request):
    user = request.user
    recipes = Recipe.objects.filter(
        favorites__user=user).select_related('author')
    recipes, active_tags = get_tag_filtered_recipes(request, recipes)
    recipes = get_recipes_for_index(recipes, user)

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/favorite.html', {
        'page': page,
        'paginator': paginator,
        'active_tags': active_tags,
    })


@login_required
def follow_index(request):
    authors = User.objects.filter(
        following__user=request.user).prefetch_related('recipes').annotate(
        recipes_count=Count('recipes'))

    paginator = Paginator(authors, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/myFollow.html', {
        'page': page,
        'paginator': paginator,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    recipes, active_tags = get_tag_filtered_recipes(request, recipes)

    user = request.user
    is_follow = False
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)
        is_follow = Follow.objects.filter(user=user, author=author).exists()

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/authorRecipe.html', {
        'author': author,
        'is_follow': is_follow,
        'page': page,
        'paginator': paginator,
        'active_tags': active_tags,
    })


@login_required
def new_recipe(request):
    form = RecipeForm(request.POST or None, files=request.FILES or None, )
    recipe_tags = ingredients = []
    if request.method == 'POST':
        recipe_tags = get_tags_from_request(request)
        ingredients, form = get_ingredients_from_request(request, form)

    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.save()
        save_ingredients_and_tags(recipe, ingredients, recipe_tags)
        return redirect('recipe', recipe.id)
    return render(request, 'recipes/formRecipe.html', {
        'form': form,
        'ingredients': ingredients,
        'recipe_tags': recipe_tags,
        'new_recipe': True,
    })


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
    if request.method != 'POST':
        ingredients = get_ingredients_from_recipe(recipe)
        recipe_tags = recipe.tags.all()
    else:
        recipe_tags = get_tags_from_request(request)
        ingredients, form = get_ingredients_from_request(request, form)

    if form.is_valid():
        recipe = form.save()
        save_ingredients_and_tags(recipe, ingredients, recipe_tags)
        return redirect('recipe', recipe.id)
    return render(request, 'recipes/formRecipe.html', {
        'form': form,
        'ingredients': ingredients,
        'recipe_tags': recipe_tags,
        'recipe_id': recipe_id,
    })


@login_required
def recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.author != request.user:
        return redirect('recipe', recipe_id)
    title = recipe.title
    recipe.delete()
    return render(request, 'recipes/recipe_delete_done.html', {
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


@login_required
def shop_list(request):
    recipes = Recipe.objects.filter(purchases__user=request.user)
    return render(request, 'recipes/shopList.html', {
        'recipes': recipes,
    })


@login_required
def shop_list_download(request):
    ingredients_sum = {}
    recipes = Recipe.objects.filter(purchases__user=request.user)
    ingredients = RecipeIngredient.objects.filter(
        recipe__in=recipes
    ).values_list(
        'ingredient__title',
        'quantity',
        'ingredient__dimension',
        named=True
    )

    for ingredient in ingredients:
        title = ingredient.ingredient__title
        if title not in ingredients_sum:
            ingredients_sum[title] = {
                'quantity': ingredient.quantity,
                'dimension': ingredient.ingredient__dimension, }
        else:
            ingredients_sum[title]['quantity'] += ingredient.quantity
    return FileResponse(
        get_shop_list_pdf_binary(ingredients_sum),
        filename='Shop_list.pdf',
        as_attachment=True
    )
