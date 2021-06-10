from django import template
from django.http import QueryDict

from ..models import Tag

register = template.Library()


@register.filter
def add_class(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def get_request_params(request, tag):
    """Возвращает закодированную строку параметров для фильтрации по тегам."""
    tags = request.GET.getlist('tags')
    if not tags:
        # Если в запросе нет тегов, значит считаем, что выбраны все теги
        tags = [str(tag.id) for tag in Tag.objects.all()]
    if str(tag.id) not in tags:
        tags.append(tag.id)
    else:
        # убираем все повторения этого тега
        tags = [tag_id for tag_id in tags if tag_id != str(tag.id)]
    if not tags:
        return ''
    result = QueryDict(mutable=True)
    result.setlist('tags', tags)
    return f'?{result.urlencode()}'
