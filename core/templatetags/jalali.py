from django import template
from core.jalali import to_jalali

register = template.Library()


@register.filter
def jalali(value):
    return to_jalali(value, with_time=hasattr(value, 'hour'))
