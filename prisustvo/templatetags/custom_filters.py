from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def slugify_status(status):
    return ''.join(filter(str.isalnum, status))

@register.filter
def div(value, arg):
    try:
        return (int(value) / int(arg)) * 100
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
