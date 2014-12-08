# -*- coding: utf-8 -*-
from django_tables2.columns.base import Column, library
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

@library.register
class ButtonListColumn(Column):
    """
    renders a list of bootstrap buttons
    """
    buttons = []
    width = 25
    padding = 5

    #def __init__(self, button_conf, urlconf=None, args=None, kwargs=None,
    #             current_app=None, attrs=None, **extra):
    def __init__(self, *args, **kwargs):
        self.buttons = kwargs.pop('buttons')
        super(ButtonListColumn, self).__init__(*args, **kwargs)

    def prepare_btn(self, btn, value, bound_column):
        keys = btn.keys()
        if 'target' in keys:
            btn['target'] = u'target="%s"' % btn['target']
        else:
            btn['target'] = u''
        if 'label' in keys:
            btn['label'] = 'title="%s"' % btn['label']
        else:
            btn['label'] = u''
        if 'view' in keys:
            btn['url'] = reverse(btn['view'], kwargs={
                bound_column.accessor: value })
        else:
            btn['view'] = u''
        return btn

    def render(self, value, record, bound_column):
        _rendered = []
        for btn in self.buttons:
            _btn = self.prepare_btn(btn.copy(), value, bound_column)
            if 'method_available' in _btn:
                if not getattr(record, _btn['method_available'])():
                    continue
            _rendered.append(u'<a href="%(url)s" ' \
                u'class="btn btn-condensed %(css)s"' \
                u' %(target)s %(label)s><span class="glyphicon glyphicon-' \
                u'%(icon)s"></span></a>' % _btn)
        return mark_safe(u'\n'.join(_rendered))
