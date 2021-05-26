from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Color(models.TextChoices):
    ORANGE = 'orange', 'Оранжевый'
    GREEN = 'green', 'Зеленый'
    PURPLE = 'purple', 'Фиолетовый'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=50,
        unique=True,
    )
    # get_color_display() - получить удобно читаемый цвет
    color = models.CharField(
        verbose_name='Цвет',
        max_length=20,
        choices=Color.choices,
        default=Color.GREEN,
    )


class Ingredient(models.Model):
    title = models.CharField(
        verbose_name='Название ингредиента',
        max_length=50,
    )
    unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    title = models.CharField(
        verbose_name='Название рецепта',
        max_length=100,
    )
    description = models.TextField(
        verbose_name='Описание рецепта',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True,
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='recipes/',
        help_text='Можете добавить картинку',
        blank=True,
        null=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(0)],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент',
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    quantity = models.DecimalField(
        verbose_name='Количество',
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0)]
    )