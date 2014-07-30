# -*- coding: utf-8 -*-
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.http import HttpResponse
from django.views.generic import View
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_tables2 import RequestConfig
from copy import deepcopy
import importlib, json, random, datetime
from collections import OrderedDict


class MainMenuMixin(object):

    def get_context_data(self, *args, **kwargs):
        ctx = super(MainMenuMixin, self).get_context_data(*args, **kwargs)
        ctx['mainmenu'] = self.mainmenu
        return ctx


#class LogMixin(object):
#    """
#    LogMixin implements Logging for
#    DB Object Creation, Updating and Deletetion.
#
#    Use for DB-Logs only, not for System or Message logs.
#    """
#    def form_valid(self, form):
#        obj = super(LogMixin, self).form_valid(form)
#        if isinstance(self, CreateView):
#            LogAction.log_database_add(self.object, self.request.user)
#        if isinstance(self, UpdateView):
#            LogAction.log_database_update(self.object, self.request.user)
#        if isinstance(self, DeleteView):
#            LogAction.log_database_delete(self.object, self.request.user)
#        return obj


class GenericModelMixin(object):
    """
    Attributes & methods that are used from
    * GenericTableMixin
    * GenericCrudMixin
    """
    template_name = 'administration/base.html'
    selected = None
    filter_form = None

    def get_breadcrumbs(self):
        list_view = 'admin-%s-list' % self.get_model_name().lower()
        return [
            {
                'url': reverse_lazy(list_view),
                'label': self.get_verbose_name()
            }
        ]

    def get_model(self):
        return self.model

    def get_class_name(self):
        return self.get_model().__name__

    def get_model_name(self):
        return self.get_model()._meta.model_name

    def get_verbose_name(self):
        return self.get_model()._meta.verbose_name

    def get_app_label(self):
        return self.get_model()._meta.app_label

    def get_verbose_name_plural(self):
        return self.get_model()._meta.verbose_name_plural

    def get_title(self):
        return u'(unknown)'

    def get_context_data(self, *args, **kwargs):
        ctx = super(GenericModelMixin, self).get_context_data(
            *args, **kwargs)
        ctx['title'] = self.get_title()
        ctx['selected'] = self.selected
        ctx['breadcrumbs'] = self.get_breadcrumbs()
        return ctx

    def get_template_names(self):
        if hasattr(self, 'template_name'):
            if isinstance(self.template_name, basestring):
                return [self.template_name]
        filename = self.template_name_suffix.replace('_', '')
        return ["administration/%(model)s/%(filename)s.html" % {
            'model': self.get_model_name(),
            'filename': filename
        }]


class GenericTableMixin(GenericModelMixin):
    """
    Generic View-mixin for all list-/table-related views

    IMPORTANT! Do not set table_class attribute here:
    hasattr(self, 'table_class') returns True, even if you set:
    table_class = None or
    table_class = False
    """
    filter_conf = None

    def get_queryset(self):
        qs = super(GenericTableMixin, self).get_queryset()
        if not hasattr(self, 'filter_set'):
            return qs
        if self.filter_set is None:
            return qs
        self.filter_conf = self.filter_set(self.request.GET, queryset=qs)
        return self.filter_conf.qs

    def get_table_class(self):
        if hasattr(self, 'table_class'):
            return self.table_class
        module_name = '%s.tables' % self.get_app_label()
        module = importlib.import_module(module_name)
        return getattr(module, '%sTable' % self.get_class_name())

    def get_table(self):
        table_class = self.get_table_class()
        if table_class:
            table = table_class(self.get_queryset())
            RequestConfig(self.request).configure(table)
            return table
        return None

    def get_context_data(self, *args, **kwargs):
        ctx = super(GenericTableMixin, self).get_context_data(*args, **kwargs)
        ctx['table'] = self.get_table()
        ctx['menues'] = self.get_menues()
        ctx['filter_conf'] = self.filter_conf
        return ctx

    def get_menues(self):
        return [{
            'css': 'btn-success',
            'href': reverse_lazy('admin-%s-create' % self.get_model_name()),
            'label': 'Add', }]

    def get_title(self):
        return u'List of %s' % self.get_verbose_name_plural()


class RelatedMixin(GenericModelMixin):
    """
    all attributes & methods for:
    * RelatedTableMixin
    * RelatedCrudMixin
    """
    parent = None
    parent_model = None
    parent_field = None

    def get_parent(self):
        self.parent = self.parent_model.objects.get(
            pk=self.kwargs.get('parent_pk', None))
        return self.parent

    def get_breadcrumbs(self):
        list_view = 'admin-%(parent)s-%(model)s-list' % {
            'parent': self.parent._meta.model_name.lower(),
            'model': self.get_model_name().lower()
        }
        return [
            {
                'url': reverse_lazy(list_view, kwargs={
                    'parent_pk': self.parent.pk }),
                'label': self.get_verbose_name()
            }
        ]

    def get(self, request, *args, **kwargs):
        self.get_parent()
        return super(RelatedMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_parent()
        return super(RelatedMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(RelatedMixin, self).get_context_data(*args, **kwargs)
        ctx['parent'] = self.parent
        return ctx

    def get_template_names(self):
        if hasattr(self, 'template_name'):
            if isinstance(self.template_name, basestring):
                return [self.template_name]
        filename = self.template_name_suffix.replace('_', '')
        return ["administration/%(parent)s/%(model)s/%(filename)s.html" % {
            'parent': self.parent._meta.model_name.lower(),
            'model': self.get_model_name(),
            'filename': filename
        }]


class RelatedTableMixin(RelatedMixin, GenericTableMixin):

    def get_queryset(self):
        result = super(RelatedTableMixin, self).get_queryset()
        return result.filter(**{self.parent_field: self.kwargs['parent_pk']})

    def get_menues(self):
        return [{
            'css': 'btn-success',
            'href': reverse_lazy('admin-%(parent)s-%(model)s-create' % {
                'parent': self.parent._meta.model_name.lower(),
                'model': self.get_model_name()
            }, kwargs={'parent_pk': self.parent.pk }),
            'label': 'Add', }]


#class RelatedLogMixin(RelatedMixin, GenericTableMixin):
#    model = HistoryLog
#    template_name = None
#
#    def get_queryset(self):
#        return HistoryLog.objects.filter(
#            entity_id=self.kwargs['parent_pk'],
#            entity_type__model=self.parent._meta.model_name.lower())


class GenericCrudMixin(GenericModelMixin):
    submit_button_text = _(u'Save')
    form_template = None

    def get_breadcrumbs(self):
        breadcrumbs = super(GenericCrudMixin, self).get_breadcrumbs()
        if self.object is None:
            view = 'admin-%s-create' % self.get_model_name().lower()
            url = reverse_lazy(view)
        else:
            if self.template_name_suffix == '_detail':
                view = 'admin-%s-detail' % self.get_model_name().lower()
            else:
                view = 'admin-%s-update' % self.get_model_name().lower()
            url = reverse_lazy(view, kwargs={'pk': self.object.pk })

        breadcrumbs.append({
            'url': url,
            'label': self.get_title(),
        })
        return breadcrumbs

    def get_title(self):
        if self.template_name_suffix == '_detail':
            return u'Details of %s' % self.object
        if self.object is None:
            return u'New %s' % self.get_verbose_name()

        return u'Update %s' % self.get_verbose_name()

    def get_context_data(self, *args, **kwargs):
        ctx = super(GenericCrudMixin, self).get_context_data(*args, **kwargs)
        ctx['submit_button_text'] = self.submit_button_text
        ctx['form_template'] = self.form_template
        return ctx

    def get_model(self):
        return self.model

    def get_success_url(self):
        return reverse_lazy('admin-%s-list' % self.get_model_name())

    def get(self, request, *args, **kwargs):
        if self.template_name_suffix == '_confirm_delete':
            return self.post(request, *args, **kwargs)
        return super(GenericCrudMixin, self).get(request, *args, **kwargs)


class RelatedCrudMixin(RelatedMixin, GenericModelMixin):

    # The model of the parent instance

    """
    The view name, that will be used per default in the
    get_success_url method. The default method expects
    always to parameters:
      * pk -> PK of the current instance
      * parent_pk -> PK of the parent instance
    """
    success_view_name = None
    form_template = None

    def get_context_data(self, *args, **kwargs):
        ctx = super(RelatedCrudMixin, self).get_context_data(*args, **kwargs)
        ctx['form_template'] = self.form_template
        return ctx

    def get_success_url(self):
        if self.template_name_suffix == '_confirm_delete':
            return reverse_lazy(self.success_view_name,
                kwargs={'parent_pk': self.parent.pk})

        return reverse_lazy(self.success_view_name,
            kwargs={'pk': self.object.pk,
                    'parent_pk': self.parent.pk})

    def get(self, request, *args, **kwargs):
        if self.template_name_suffix == '_confirm_delete':
            return self.post(request, *args, **kwargs)
        return super(RelatedCrudMixin, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        setattr(self.object, self.parent_field, self.parent)
        return super(RelatedCrudMixin, self).form_valid(form)


class StatsView(View):
    left = None
    right = None

    # OK
    http_method_names = [u'get']

    # OK
    LINE_CHART_CONFIG = {
        'data': [],
        'config': {
            'series': {
                'lines': { "show": True },
                'points': { "show": True }
            },
            'xaxis': {
                'ticks': []
            }
        }
    }

    # OK
    def get_queryset(self):
        """
        Returns the basic queryset
        """
        if hasattr(self, 'queryset'):
            qs = self.queryset
        if hasattr(self, 'model'):
            qs = self.model.objects.all()
        print qs.count()
        return qs

    # Non-functional
    def get_time_filtered_queryset(self):
        """
        this method should manage GET params of several input fields
        that define the time frame (e.g. "from", "until", "time range", ...)
        """
        self.right = datetime.date.today()
        self.left = self.right + datetime.timedelta(-30)
        qs = self.get_queryset().filter(created_at__range=[self.left,
                                                           self.right])
        print qs.count()
        return qs

    # TODO: this method returns random data at the moment.
    # It should ...
    # * get queryset (get_time_filtered_queryset)
    # * if necessary:
    #   * convert data types for json (e.g. Time, DateTime values, ...)
    # * return a list
    # basic implementation could be: `return list(self.get_time_filt...)`
    def get_data(self):
        """
        Return a list of [X-Axis, Value 1, Value 2, ... Value n], e.g.
        [
            ['Jun', 5.0, 7.2, 9.0],
            ['Jul', 4.0, 7.7, 0.8],
            ['Aug', 4.0, 7.7, 0.8],
        ]
        """
        qs = self.get_time_filtered_queryset()
        qs = qs.extra(select=self.select)
        return qs.values(*self.select.keys())


    # OK, Has to be configured for each implementation
    def get_legend(self):
        return ['Data row 1']

    def get_complete_dict(self, line_count):
        """
        the date range (self.left + self.right) has to be already defined
        """
        delta = self.right - self.left
        data = OrderedDict()
        for i in range(delta.days + 1):
            day = self.left + datetime.timedelta(days=i)
            data[day] = [0] * line_count
        return data

    def transform_data(self, qs):
        """
        * groups and converts data of a final queryset
        * expects a Date()-object in the first column -> x-axis
        * all other columns are handles as data lines -> [y-axis 1, 2, ...]
        """
        data = None
        for row in qs:
            row = [row[n] for n in self.select.keys()]
            if data is None:
                data = self.get_complete_dict(len(row))
            for i in range(1, len(row)):
                data[row[0]][i] += row[i]
        return [[key] + value for key, value in data.iteritems()]

    # OK
    def get_dataset(self):
        """
        Transform the final data (grouping, sorting, ...) and
        append meta data (like "legend", jqFlot settings, ...)
        """
        legends = self.get_legend()
        data = self.transform_data(self.get_data())
        dataset = deepcopy(self.LINE_CHART_CONFIG)
        for counter, legend in enumerate(legends):
            dataset['data'].append({
                'label': legend,
                'data': list(enumerate([n[counter + 1] for n in data]))
            })
        ticks = list(enumerate([n[0].strftime('%d.%m') for n in data]))
        dataset['config']['xaxis']['ticks'] = ticks
        return dataset

    # OK
    def get(self, request, *args, **kwargs):
        dataset = self.get_dataset()
        return HttpResponse(json.dumps(dataset, indent=4), 'application/json')