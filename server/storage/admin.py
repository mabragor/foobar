# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from storage import models

class CoachAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'reg_date')
    fieldsets = ((None, {'fields': ('first_name', 'last_name',
                                    'email')}),)
admin.site.register(models.Coach, CoachAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('rfid_code', 'last_name', 'first_name', 'email', 'reg_date')
    search_fields = ('rfid_code', 'last_name', 'first_name')
    fieldsets = ((None, {'fields': ('first_name', 'last_name',
                                    'email')}),)
admin.site.register(models.Client, ClientAdmin)

class RenterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'reg_date')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {'fields': ('last_name', 'first_name', 'email')}),
                 (_('Phones'), {'fields': ('phone_mobile', 'phone_work', 'phone_home')}))
admin.site.register(models.Renter, RenterAdmin)

class RentAdmin(admin.ModelAdmin):
    list_display = ('renter', 'status', 'title', 'begin_date', 'end_date', 'reg_date')
    search_fields = ('renter', 'title')
    fieldsets = ((None, {'fields': ('renter', 'paid', 'status')}),
                 (_('Info'), {'fields': ('title', 'desc')}),
                 (_('Dates'), {'fields': ('begin_date', 'end_date')}))
admin.site.register(models.Rent, RentAdmin)

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
    list_display = ('title', 'coaches', 'groups', 'price', 'duration', 'reg_date')
    ordering = ('title', 'group')
    search_fields = ('title', 'group')
    fieldsets = (
        (None, {'fields': ('title', 'duration', 'count', 'price')}),
        (_(u'Relation'), {'fields': ('group', 'coach')}),
        )

admin.site.register(models.Course, CourseAdmin)

class CardAdmin(admin.ModelAdmin):
    list_display = ('course', 'client', 'type', 'count_sold', 'count_used',
                    'price','reg_date', 'bgn_date', 'exp_date')
    ordering = ('reg_date', 'exp_date', 'count_sold', 'client')
    fieldsets = (
        (None, {'fields': ('type', 'exp_date', 'count_sold', 'price')}),
        (_('Links'), {'fields': ('course', 'client')}),
        )
admin.site.register(models.Card, CardAdmin)