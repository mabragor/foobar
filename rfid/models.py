# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

class Card(models.Model):
    code = models.CharField(max_length=8)
    reg_date = models.DateTimeField(verbose_name=_('Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Card\'s code')
        verbose_name_plural = _(u'Card codes')

    def __unicode__(self):
        return self.code
