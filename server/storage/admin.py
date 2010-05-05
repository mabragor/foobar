# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms

from storage import models

class CoachAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name',
                    'phone', 'email', 'reg_date')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {'fields': ('last_name', 'first_name',
                                    'phone', 'email',
                                    'birth_date', 'desc')}),)
admin.site.register(models.Coach, CoachAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'rfid_code',
                    'phone', 'email', 'reg_date')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {'fields': ('last_name', 'first_name',
                                    'phone', 'email',
                                    'discount', 'birth_date')}),)
admin.site.register(models.Client, ClientAdmin)

class RenterAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'phone', 'email', 'reg_date')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {'fields': ('last_name', 'first_name',
                                    'phone', 'email', 'birth_date')}),
                 (_('Phones'), {'fields': ('phone_mobile', 'phone_work', 'phone_home'),
                                'description': _(u'Fill at least one field here.')}))
admin.site.register(models.Renter, RenterAdmin)

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

class PriceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_category', 'cost', 'count', 'discount', 'special')
    ordering = ('price_category', 'special', 'cost', 'discount', 'title')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'price_category', 'cost', 'count', 'discount', 'special')}),)
admin.site.register(models.Price, PriceAdmin)

# class CardAdmin(admin.ModelAdmin):
#     list_display = ('team', 'client', 'type', 'count_sold', 'count_used',
#                     'price','reg_date', 'bgn_date', 'exp_date')
#     ordering = ('reg_date', 'exp_date', 'count_sold', 'client')
#     fieldsets = (
#         (None, {'fields': ('type', 'exp_date', 'count_sold', 'price')}),
#         (_('Links'), {'fields': ('team', 'client')}),
#         )
# admin.site.register(models.Card, CardAdmin)


### Interface for Team Model : Begin

class TeamInlineForm(forms.ModelForm):
    class Meta:
        model = models.Calendar
        exclude = ('rent')

class CalTeamItemInline(admin.TabularInline):
    model = models.Calendar
    form = TeamInlineForm
    extra = 1

class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'coach', 'price_category', 'groups',
                    'duration', 'reg_date')
    ordering = ('title',)
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('group', 'title', 'coach',
                           'duration', 'price_category')}),
        )
    inlines = [CalTeamItemInline]
admin.site.register(models.Team, TeamAdmin)

### Interface for Team Model : End


### Interface for Rent Model : Begin

class RentInlineForm(forms.ModelForm):
    class Meta:
        model = models.Calendar
        exclude = ('team')

class CalRentItemInline(admin.TabularInline):
    model = models.Calendar
    form = RentInlineForm
    extra = 1

class RentAdmin(admin.ModelAdmin):
    list_display = ('title', 'renter', 'duration',
                    'paid', 'paid_status', 'reg_date')
    search_fields = ('renter', 'title')
    fieldsets = ((None, {'fields': ('renter', 'paid', 'paid_status')}),
                 (_('Info'), {'fields': ('title', 'duration', 'desc')}))
    inlines = [CalRentItemInline]
admin.site.register(models.Rent, RentAdmin)

### Interface for Rent Model : End
