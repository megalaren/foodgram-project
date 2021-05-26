from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return self.username
