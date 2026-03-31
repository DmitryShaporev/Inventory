from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Возвращает абсолютное значение числа"""
    if value is None:
        return 0
    return abs(float(value))