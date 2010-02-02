# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

class Applied(models.Model):
    name = models.CharField(verbose_name=_(u'Name of patch'), max_length=10)
    applied = models.DateTimeField(verbose_name=_('Applied'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Patch')
        verbose_name_plural = _(u'Patches')

    def __unicode__(self):
        return self.name

