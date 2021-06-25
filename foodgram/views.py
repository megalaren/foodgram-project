from django.shortcuts import render


def page_not_found(request, exception=None):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользовательской страницы 404 не нужно
    return render(request, '404.html', {
        'path': request.path
    },
        status=404
    )


def server_error(request):
    return render(request, '500.html', status=500)
