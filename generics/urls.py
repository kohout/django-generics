# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

""" Generic stuff for url patterns """


def crud_urls(namespace,
              class_prefix,
              module,
              additional_urls=None,
              view_praefix='admin',
              url_prefix='',
              exclude_urls=[]):
    _url_confs = [
        ['ListView',   r'^%s%s/$',                       'list'],
        ['CreateView', r'^%s%s/add/$',                   'create'],
        ['UpdateView', r'^%s%s/(?P<pk>[\w-]+)/$',        'update'],
        ['DeleteView', r'^%s%s/(?P<pk>[\w-]+)/delete/$', 'delete'],
    ]
    url_confs = []

    # remove default views, if explicitly defined
    for _url_conf in _url_confs:
        if not _url_conf[2] in exclude_urls:
            url_confs.append(_url_conf)

    # add additional views, if excplicitly defined
    if additional_urls:
        url_confs.extend(additional_urls)
    _patterns = None
    for url_conf in url_confs:
        _view_class = getattr(module, u''.join([
            class_prefix, url_conf[0]]))
        _new_pattern = url(
            url_conf[1] % (url_prefix, namespace),
            _view_class.as_view(),
            name=u'-'.join([view_praefix, namespace, url_conf[2]]))
        if _patterns is None:
            _patterns = patterns('', _new_pattern)
        else:
            _patterns += patterns('', _new_pattern)

    return _patterns


def append_1n_urls(class_name,
                   view_name_prefix,
                   available_views=['list', 'update', 'create', 'delete']):
    l = class_name.lower()
    prefix = r'^/%s/'
    pattern_list = []
    if 'list' in available_views:
        pattern_list.append(['%sListView' % view_name_prefix,
            prefix + r'(?P<parent_pk>[\w-]+)/%s/$' % l,
            '%s-list' % l])
    if 'update' in available_views:
        pattern_list.append(['%sUpdateView' % view_name_prefix,
            prefix + r'(?P<parent_pk>[\w-]+)/%s/(?P<pk>[\w-]+)/update/$' % l,
            '%s-update' % l])
    if 'create' in available_views:
        pattern_list.append(['%sCreateView' % view_name_prefix,
            prefix + r'(?P<parent_pk>[\w-]+)/%s/create/$' % l,
            '%s-create' % l])
    if 'delete' in available_views:
        pattern_list.append(['%sDeleteView' % view_name_prefix,
            prefix + r'(?P<parent_pk>[\w-]+)/%s/(?P<pk>[\w-]+)/delete/$' % l,
            '%s-delete' % l])
    return pattern_list
