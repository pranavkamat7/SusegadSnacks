from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field  # Return unchanged if it's not a form field


@register.filter
def split(value, key):
    return value.split(key)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))