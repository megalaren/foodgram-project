# Generated by Django 3.2.3 on 2021-06-03 09:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_alter_recipeingredient_recipe'),
        ('api', '0002_rename_favorites_favorite'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('recipe', 'user')},
        ),
    ]
