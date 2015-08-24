# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.views.generic import View
from copy import deepcopy
import json, datetime
from collections import OrderedDict

class StatsView(View):
    left = None
    right = None

    days = 30
    date_field = 'created_at'

    # OK
    http_method_names = [u'get']

    # OK
    LINE_CHART_CONFIG = {
        'data': [],
        'config': {
            'series': {
                'lines': {"show": True},
                'points': {"show": True}
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
        return qs

    # Non-functional
    def get_time_filtered_queryset(self, **kwargs):
        """
        this method should manage GET params of several input fields
        that define the time frame (e.g. "from", "until", "time range", ...)
        """
        self.right = datetime.date.today()
        self.left = self.right + datetime.timedelta(-self.days)
        self.right = self.right + datetime.timedelta(1)
        time_filter = {
            '%s__range' % self.date_field: [self.left, self.right]
        }
        qs = self.get_queryset().filter(**time_filter)
        print qs.count()
        return qs

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
            # date, failed_login, success_login
            ['Jun', 5.0, 7.2, 9.0],
            ['Jul', 4.0, 7.7, 0.8],
            ['Aug', 4.0, 7.7, 0.8],
        ]
        """
        qs = self.get_time_filtered_queryset()
        qs = qs.extra(select=self.select)
        _data = qs.values(*self.select.keys())
        return _data


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
        keys = self.select.keys()
        data = self.get_complete_dict(len(keys) - 1)
        for row in qs:
            row = [row[n] for n in keys]
            for i in range(0, len(row) - 1):
                data[row[0]][i] += row[i + 1]
        return [[key] + value for key, value in data.iteritems()]

    # OK
    def get_dataset(self, **kwargs):
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
