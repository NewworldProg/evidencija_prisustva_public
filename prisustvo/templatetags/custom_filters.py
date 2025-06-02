from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def slugify_status(value):
    """
    Pretvara specijalne statuse u validna CSS imena,
    bez uklanjanja ćirilice.
    """
    if value == '+':
        return 'plus'
    if value is None or value == '':
        return 'empty'
    return value  # ostavlja ćirilicu kao što je
