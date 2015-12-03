# -*- coding: utf-8 -*-
from django_tables2.columns.base import Column, library
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

@library.register
class ButtonListColumn(Column):
    """
    renders a list of bootstrap buttons
    """
    ROW_WRAPPER = u'%s'
    ROW_TEMPLATE = u'<a href="%(url)s" ' \
                u'class="btn btn-condensed %(css)s"' \
                u' %(target)s %(label)s><span class="%(icon-prefix)s' \
                u'%(icon)s"></span></a>'

    buttons = []
    width = 25
    padding = 5

    #def __init__(self, button_conf, urlconf=None, args=None, kwargs=None,
    #             current_app=None, attrs=None, **extra):
    def __init__(self, *args, **kwargs):
        self.buttons = kwargs.pop('buttons')
        self.ROW_WRAPPER = kwargs.pop('row_wrapper', '%s')
        super(ButtonListColumn, self).__init__(*args, **kwargs)

    def prepare_btn(self, btn, value, bound_column, record):
        keys = btn.keys()
        if not 'icon' in keys:
            btn['icon'] = u''
        if not 'icon-prefix' in keys:
            btn['icon-prefix'] = 'glyphicon glyphicon-'
        if not 'css' in keys:
            btn['css'] = u''
        if 'target' in keys:
            btn['target'] = u'target="%s"' % btn['target']
        else:
            btn['target'] = u''
        if not 'button_text' in keys:
            btn['button_text'] = btn['label']
        if 'label' in keys:
            btn['label'] = 'title="%s"' % unicode(btn['label'])
        else:
            btn['label'] = u''
        if 'view' in keys:
            if 'accessor' in keys:
                btn['url'] = reverse(btn['view'], kwargs={
                    btn['accessor']: value })
            else:
                btn['url'] = reverse(btn['view'], kwargs={
                    bound_column.accessor: value })
        else:
            btn['view'] = u''
        return btn

    def render(self, value, record, bound_column):
        _rendered = []
        for btn in self.buttons:
            _btn = self.prepare_btn(btn.copy(), value, bound_column, record)
            if 'method_available' in _btn:
                if not getattr(record, _btn['method_available'])():
                    continue
            _rendered.append(self.ROW_TEMPLATE % _btn)
        return mark_safe(self.ROW_WRAPPER % u'\n'.join(_rendered))
