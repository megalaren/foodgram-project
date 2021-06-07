from django import forms
from django.contrib.auth import get_user_model

from .models import Recipe

User = get_user_model()


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'description', 'tags', 'image', 'cooking_time',
                  'ingredients',)
        # labels = {
        #     'group': 'Группа',
        #     'text': 'Текст',
        #     'image': 'Картинка'
        # }
