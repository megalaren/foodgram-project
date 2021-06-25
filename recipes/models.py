from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Color(models.TextChoices):
    ORANGE = 'orange', 'Оранжевый'
    GREEN = 'green', 'Зеленый'
    PURPLE = 'purple', 'Фиолетовый'


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Имя тега',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug',
    )
    # get_color_display() - получить удобно читаемый цвет
    color = models.CharField(
        choices=Color.choices,
        default=Color.GREEN,
        max_length=20,
        verbose_name='Цвет',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название ингредиента',
    )
    dimension = models.CharField(
        max_length=50,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название рецепта',
    )
    description = models.TextField(
        verbose_name='Описание рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes',
        verbose_name='Теги',
    )
    image = models.ImageField(
        help_text='Можете добавить картинку',
        upload_to='recipes/',
        verbose_name='Картинка',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='Время приготовления в минутах',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        through='RecipeIngredient',
        verbose_name='Ингредиент',
    )

    @admin.display(description='Теги')
    def get_tags(self):
        result = ''
        for tag_name in self.tags.values_list('name', flat=True):
            result += tag_name + '\n'
        return result

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_count',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    quantity = models.PositiveSmallIntegerField(
        null=True,
        validators=[
            MinValueValidator(0)],
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe', ],
                name='unique_ingredient_in_recipe'),
        ]
        verbose_name = 'Связь рецепт-ингредиент'
        verbose_name_plural = 'Связи рецепт-ингредиент'

    @admin.display()
    def dimension(self):
        return self.ingredient.dimension

    def __str__(self):
        return f'[{self.recipe}, {self.ingredient}, {self.quantity}]'
