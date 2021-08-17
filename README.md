![Status workflow](https://github.com/megalaren/foodgram-project/actions/workflows/foodgram.yaml/badge.svg)

## Проект FoodGram
Онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.  


### Инструкция по установке и запуску проекта
Проект автоматически разворачивается на сервере при пуше в ветку *master*.
При первом запуске на сервере необходимо проделать следующее:
- Установите docker. Инструкция по установке есть 
в [официальной документации Docker](https://docs.docker.com/engine/install/ubuntu/).
- Копировать папку *nginx* и файл *docker-compose.yaml* на сервер в домашнюю директорию.
- В домашней директории создайте файл *.env*, в котором укажите переменные окружения.
  Необходимые переменные указаны в файле *.env.example*.
- Сделайте пуш в ветку *master*, чтобы запустился workflow. 
  По его окончанию на сервере будет запущен проект.
- Далее на сервере перейдите в контейнер web:   
```sudo docker-compose exec web bash```
- Запустите миграции:  
```python manage.py migrate --noinput```
- Загрузите данные в базу данных:  
```python manage.py loaddata fixtures.json```
- Создайте суперпользователя:  
```python manage.py createsuperuser```
- Соберите статику:  
```python manage.py collectstatic --no-input```
- Копировать картинки:  
```cp -r static/images/recipes/ media/```

Теперь проект полностью готов.
***
### Об авторе  
Брюшинин Алексей  
<megalaren@mail.ru>

### Используемые технологии 
- [Python 3.8.5](https://www.python.org/)
- [Django 3.2.4](https://www.djangoproject.com/)
- [Django REST framework 3.12.4](https://www.django-rest-framework.org/)
- [Nginx](https://nginx.org/)
- [Gunicorn 20.0.4](https://gunicorn.org/)
- [PostgreSQL 12.4](https://www.postgresql.org/)
- [Docker 20.10.6](https://www.docker.com/)
