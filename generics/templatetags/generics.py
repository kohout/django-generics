# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.simple_tag
def icon(icon_class):
    """
    Render an icon
    """
    return '<span class="{icon}"></span>'.format(icon=icon_class)

@register.filter
def percentage(value):
    """
    returns a percentage value (between 0 and 100)
    """
    return value * 100.0

@register.filter
def row_button_width(row_buttons):
    """
    returns the width of the row buttons
    """
    if not row_buttons:
        return 0
    n = len(row_buttons)
    return n * 25 + (n - 1) * 5

@register.filter
def pass_param(method, param):
    return method(param)
