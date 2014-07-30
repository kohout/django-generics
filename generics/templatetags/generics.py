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
