from django import template

from ..models import Tag

register = template.Library()


@register.filter
def add_class(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def get_all_tags(request):
    return Tag.objects.all()


@register.filter
def get_tags_params(request, tag):
    """Возвращает закодированную строку параметров для фильтрации по тегам."""
    result = request.GET.copy()
    tags = result.getlist('tags')
    if not tags:
        # Если в запросе нет тегов, значит считаем, что выбраны все теги
        tags = [
            str(tag_id) for tag_id in Tag.objects.values_list('id', flat=True)
        ]
    if str(tag.id) not in tags:
        tags.append(str(tag.id))
    else:
        # убираем все повторения этого тега
        tags = [tag_id for tag_id in tags if tag_id != str(tag.id)]
    result.setlist('tags', tags)
    if not result:
        return ''
    return f'?{result.urlencode()}'


@register.filter
def get_page_param(request, page):
    """Возвращает закодированную строку параметров для пагинации."""
    result = request.GET.copy()
    result['page'] = page
    return f'?{result.urlencode()}'
