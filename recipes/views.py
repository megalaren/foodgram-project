from django.contrib.auth import get_user_model
from django.shortcuts import render


User = get_user_model()


def index(request):
    user = request.user
    return render(request, 'recipes/indexAuth.html')
