import io
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef
from fpdf import FPDF

from .models import Ingredient, RecipeIngredient, Tag
from api.models import Favorite, Purchase


INVALID_QUANTITY = 'Неправильно задано количество у ингредиента {title}.'
INGREDIENT_DOES_NOT_EXIST = 'Ингредиента {title} не существует.'
INGREDIENT_ADDED = 'Ингредиент {title} добавлен в рецепт больше одного раза.'


# настройки PDF
BOTTOM_MARGIN = 15
FONT_SIZE = 14
HEIGHT = 8
TOP_MARGIN = 15
LEFT_MARGIN = 15
fonts = os.path.join(settings.BASE_DIR, 'fonts')
FONT_FILE = os.path.join(fonts, 'DejaVuSansCondensed.ttf')
BOLD_FONT_FILE = os.path.join(fonts, 'DejaVuSansCondensed-Bold.ttf')


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


def get_shop_list_pdf_binary(ingredients):
    """Возвращает список покупок pdf в виде двоичных данных."""
    keys = sorted(ingredients.keys())
    pdf = FPDF()
    pdf.add_font('DejaVu', '', FONT_FILE, uni=True)
    pdf.add_font('DejaVu', 'B', BOLD_FONT_FILE, uni=True)
    pdf.set_top_margin(TOP_MARGIN)
    pdf.set_left_margin(LEFT_MARGIN)
    pdf.set_auto_page_break(True, BOTTOM_MARGIN)

    pdf.add_page()
    pdf.set_font('DejaVu', 'B', FONT_SIZE + 2)
    pdf.cell(180, HEIGHT, 'Список покупок', 0, 1, 'C', )
    pdf.cell(180, HEIGHT, '', 0, 1, 'C', )
    pdf.set_font('DejaVu', '', FONT_SIZE)

    for index, title in enumerate(keys):
        pdf.cell(10, HEIGHT, f'{index + 1}.', 1, 0, 'C', )
        pdf.cell(140, HEIGHT, title, 1, 0, 'L', )

        text = f'{ingredients[title]["quantity"]} {ingredients[title]["dimension"]}'
        pdf.cell(30, HEIGHT, text, 1, 1, 'C', )

    pdf.cell(180, HEIGHT, '', 0, 1, 'C', )
    pdf.set_font('DejaVu', '', FONT_SIZE - 2)
    pdf.cell(180, HEIGHT, 'Создано на сайте foodgram', 0, 1, 'R', )

    if pdf.state < 3:
        pdf.close()
    return io.BytesIO(pdf.buffer.encode('latin1'))
