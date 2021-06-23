![Status workflow](https://github.com/megalaren/yamdb_final/actions/workflows/yamdb_workflow.yaml/badge.svg)

## Проект FoodGram


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
<aleksei.briushinin@yandex.ru>

### Используемые технологии 
- [Python 3.8.5](https://www.python.org/)
- [Django 3.0.5](https://www.djangoproject.com/)
- [Django REST framework 3.11.0](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Nginx](https://nginx.org/)
- [Gunicorn 20.0.4](https://gunicorn.org/)
- [PostgreSQL 12.4](https://www.postgresql.org/)
- [Docker 20.10.6](https://www.docker.com/)

### Лицензия
[BSD-3-Clause License](https://github.com/megalaren/infra_sp2/blob/master/LICENSE)
