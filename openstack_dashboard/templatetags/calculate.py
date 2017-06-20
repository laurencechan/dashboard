from django import template
register = template.Library()

@register.filter(name='subtraction')
def subtraction(reduction, minuend):
    return reduction - minuend
