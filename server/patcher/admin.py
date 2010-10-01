# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from patcher import models

class AppliedAdmin(admin.ModelAdmin):
    list_display = ('name', 'applied')
    fieldsets = ((None, {'fields': ()}),)
admin.site.register(models.Applied, AppliedAdmin)
models.Applied.description = _(u'This model consists of records of patches which had been applied on database. ')
