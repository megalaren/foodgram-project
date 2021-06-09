from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef

from .models import Ingredient, RecipeIngredient, Tag
from api.models import Favorite, Purchase


INVALID_QUANTITY = 'Неправильно задано количество у ингредиента {title}.'
INGREDIENT_DOES_NOT_EXIST = 'Ингредиента {title} не существует.'
INGREDIENT_ADDED = 'Ингредиент {title} добавлен в рецепт больше одного раза.'


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


def get_tags_from_request(request, all_tags):
    """Возвращает тэги из all_tags, slug которых есть в request."""
    slugs_of_tags = [tag.slug for tag in all_tags]
    keys = [key for key in request.POST if key in slugs_of_tags]
    return Tag.objects.filter(slug__in=keys)


def get_ingredients_from_recipe(recipe):
    """Получает из recipe ингредиенты, их количество и id для шаблона."""
    ingredients = []
    ingredient_index = 1
    recipe_ingredients = recipe.ingredients_count.all()

    for recipe_ingredient in recipe_ingredients:
        ingredients.append({
            'id': ingredient_index,
            'ingredient': recipe_ingredient.ingredient,
            'quantity': recipe_ingredient.quantity,
        })
        ingredient_index += 1
    return ingredients


def get_ingredients_from_request(request, form):
    """Получает из request ингредиенты, их количество и id для шаблона.

    Добавляет ошибки в форму.
    """
    ingredients = []
    added_ingredients = []  # Для контроля уже добавленных ингредиентов
    data = request.POST

    for key in data:
        if not key.startswith('nameIngredient'):
            continue
        ingredient_index = key.strip('nameIngredient_')
        quantity_str = data.get(f'valueIngredient_{ingredient_index}')
        if not quantity_str.isdigit():
            # Неправильно задано количество
            form.add_error(
                field='ingredients',
                error=ValidationError(
                    INVALID_QUANTITY.format(title=data.get(key)))
            )
            continue
        quantity = int(quantity_str)
        try:
            ingredient = Ingredient.objects.get(title=data.get(key))
        except Ingredient.DoesNotExist:
            # Не существует ингредиента в БД
            form.add_error(
                field='ingredients',
                error=ValidationError(
                    INGREDIENT_DOES_NOT_EXIST.format(title=data.get(key)))
            )
            continue
        ingredients.append({
            'id': ingredient_index,
            'ingredient': ingredient,
            'quantity': quantity,
        })
        if ingredient.id in added_ingredients:
            # Ингредиент добавлен в рецепт несколько раз
            form.add_error(
                field='ingredients',
                error=ValidationError(
                    INGREDIENT_ADDED.format(title=data.get(key)))
            )
        added_ingredients.append(ingredient.id)
    return ingredients, form


def save_ingredients_and_tags(recipe, ingredients, tags):
    """Сохраняет тэги и ингредиенты в рецепт."""
    recipe.tags.clear()
    recipe.ingredients.clear()
    for tag in tags:
        recipe.tags.add(tag)
    for ingredient in ingredients:
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient['ingredient'],
            quantity=ingredient['quantity'],
        )
