# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from patcher import models

class AppliedAdmin(admin.ModelAdmin):
    list_display = ('name', 'applied')
    fieldsets = ((None, {'fields': ()}),)
admin.site.register(models.Applied, AppliedAdmin)
