# -*- coding: utf-8 -*-

class StackedBar(object):
    """
    a helper class for presenting a stacked bar with different styles (e.g. colors)
    """
    items = []
    total_width = 100
    total_value = 0.0

    def __init__(self, items):
        self.items = items
        self.calc_items()

    def calc_items(self):
        for item in self.items:
            self.total_value += abs(item.value)
        for item in self.items:
            item.normalize(self.total_value,
                           self.total_width)


class StackedBarItem(object):
    css = None
    label = None
    value = 0.0
    width = 0.0

    def __init__(self, **kwargs):
        self.css = kwargs.get('css', None)
        self.label = kwargs.get('label', None)
        self.value = kwargs.get('value', 0.0)

    def normalize(self, total_value, total_width):
        if total_value == 0:
            return
        self.width = int(round(
            float(total_width) * self.value / total_value, 0))
