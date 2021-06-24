from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from api.models import Favorite, Follow, Purchase

from .forms import RecipeForm
from .models import Recipe, Tag
from .utils import (get_ingredients_from_recipe, get_ingredients_from_request,
                    get_recipes_for_index, get_shop_list_pdf_binary,
                    get_tag_filtered_recipes, get_tags_from_request,
                    save_ingredients_and_tags)

User = get_user_model()

PER_PAGE = 6


def index(request):
    recipes = Recipe.objects.select_related('author')
    all_tags = Tag.objects.all()
    recipes, active_tags = get_tag_filtered_recipes(request, recipes, all_tags)
    user = request.user
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/index.html', {
        'page': page,
        'paginator': paginator,
        'all_tags': all_tags,
        'active_tags': active_tags,
    })


@login_required
def favorite(request):
    user = request.user
    recipes = Recipe.objects.filter(
        favorites__user=user).select_related('author')
    all_tags = Tag.objects.all()
    recipes, active_tags = get_tag_filtered_recipes(request, recipes, all_tags)
    recipes = get_recipes_for_index(recipes, user)

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/favorite.html', {
        'page': page,
        'paginator': paginator,
        'all_tags': all_tags,
        'active_tags': active_tags,
    })


@login_required
def follow_index(request):
    authors = User.objects.filter(
        following__user=request.user).prefetch_related('recipes').annotate(
        recipes_count=Count('recipes'))
    all_tags = Tag.objects.all()

    paginator = Paginator(authors, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/myFollow.html', {
        'page': page,
        'paginator': paginator,
        'all_tags': all_tags,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    all_tags = Tag.objects.all()
    recipes, active_tags = get_tag_filtered_recipes(request, recipes, all_tags)

    user = request.user
    is_follow = False
    if user.is_authenticated:
        recipes = get_recipes_for_index(recipes, user)
        is_follow = Follow.objects.filter(user=user, author=author).exists()

    paginator = Paginator(recipes, PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'recipes/authorRecipe.html', {
        'all_tags': all_tags,
        'author': author,
        'is_follow': is_follow,
        'page': page,
        'paginator': paginator,
        'active_tags': active_tags,
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


@login_required
def shop_list(request):
    recipes = Recipe.objects.filter(purchases__user=request.user)
    return render(request, 'recipes/shopList.html', {
        'recipes': recipes,
    })


@login_required
def shop_list_download(request):
    ingredients = {}
    recipes = Recipe.objects.filter(purchases__user=request.user)
    for recipe in recipes:
        for recipe_ingredient in recipe.ingredients_count.all():
            title = recipe_ingredient.ingredient.title
            if title not in ingredients:
                ingredients[title] = {
                    'quantity': recipe_ingredient.quantity,
                    'dimension': recipe_ingredient.ingredient.dimension,
                }
            else:
                ingredients[title]['quantity'] += recipe_ingredient.quantity

    return FileResponse(
        get_shop_list_pdf_binary(ingredients),
        filename='Shop_list.pdf',
        as_attachment=True
    )


def page_not_found(request, exception=None):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 не нужно
    return render(request, '404.html', {
        'path': request.path
    },
        status=404
    )


def server_error(request):
    return render(request, '500.html', status=500)
