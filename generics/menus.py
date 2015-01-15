# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from copy import copy

MENUS = getattr(settings, 'GENERICS_MENUS', {})

MENU_INDEX = getattr(settings, 'GENERICS_MENU_INDEX', {})


class Node(object):
    key = None
    url = None
    label = None
    title = None
    attrs = None

    menu = None
    rootline = []
    nodes = OrderedDict()

    def get_rootline(self):
        breadcrumb = copy(self.rootline)
        breadcrumb.reverse()
        return breadcrumb

    def get_children(self):
        return [(n, False) for n in self.nodes.values()]

    def get_current_level(self):
        if not len(self.rootline):
            return []
        parent = self.rootline[-1]
        return [(n, n == self) for n in parent.nodes.values()]

    def append(self, new_node):
        new_node.menu = self.menu
        new_node.rootline = self.rootline + [self]
        new_node.update_menu_index()
        self.nodes.update({ new_node.key: new_node })

    @property
    def identifier(self):
        if self.menu and self.key:
            return '.'.join([self.menu, self.key])
        return ''

    def update_menu_index(self):
        if self.identifier:
            MENU_INDEX[self.identifier] = self

    def __init__(self, **kwargs):
        self.key = kwargs['key']
        self.label = kwargs['label']
        self.url = kwargs.get('url', None)
        self.title = kwargs.get('title', None)
        self.attrs = kwargs.get('attrs', None)

        # 1. set menu (INFO: order is important!)
        _menu = kwargs.get('menu', None)
        if _menu:
            self.menu = _menu
            MENUS[_menu] = self
        self.update_menu_index()

        # 2. check rootline
        if not len(self.rootline):
            self.rootline.append(self)

        # 3. append child nodes
        for node in kwargs.get('nodes', []):
            self.append(node)

        setattr(settings, 'GENERICS_MENUS', MENUS)
        setattr(settings, 'GENERICS_MENU_INDEX', MENU_INDEX)
