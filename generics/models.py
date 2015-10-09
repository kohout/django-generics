# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
        verbose_name=_(u'Created at'))
    changed_at = models.DateTimeField(auto_now=True,
        verbose_name=_(u'Changed at'))

    class Meta:
        abstract = True
