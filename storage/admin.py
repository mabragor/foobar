# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from storage import models

class CoachAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'reg_date')
    fieldsets = ((None, {'fields': ('first_name', 'last_name',
                                    'email')}),)
admin.site.register(models.Coach, CoachAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('rfid_code', 'first_name', 'last_name', 'email', 'reg_date')
    search_fields = ('rfid_code', 'first_name')
    fieldsets = ((None, {'fields': ('first_name', 'last_name',
                                    'email')}),)
admin.site.register(models.Client, ClientAdmin)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'color')
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'color')}),)
admin.site.register(models.Room, RoomAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', )
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', )}),)
admin.site.register(models.Group, GroupAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'coaches', 'groups', 'duration', 'reg_date')
    ordering = ('title', 'group')
    search_fields = ('title', 'group')
    fieldsets = (
        (None, {'fields': ('title', 'duration')}),
        (_(u'Relation'), {'fields': ('group', 'coach')}),
        )

admin.site.register(models.Course, CourseAdmin)

class CardAdmin(admin.ModelAdmin):
    list_display = ('course', 'client', 'count', 'reg_date', 'exp_date')
    ordering = ('reg_date', 'exp_date', 'count', 'client')
    fieldsets = (
        (None, {'fields': ('exp_date', 'count')}),
        (_('Links'), {'fields': ('course', 'client')}),
        )
admin.site.register(models.Card, CardAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'begin')
    ordering = ('course', 'begin')
    search_fields = ('course',)
    fieldsets = ((None, {'fields': ('course', 'begin')}),)
admin.site.register(models.Schedule, ScheduleAdmin)

class ActionAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'card', 'when')
    fieldsets = ((None, {'fields': ('schedule', 'card', 'when')}),)
admin.site.register(models.Action, ActionAdmin)
