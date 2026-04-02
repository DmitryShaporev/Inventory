from datetime import datetime

from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Возвращает абсолютное значение числа"""
    if value is None:
        return 0
    return abs(float(value))

@register.filter
def format_date(date_str):
    """Преобразует строку YYYY-MM-DD в DD.MM.YYYY"""
    if not date_str:
        return ''
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except:
        return date_str