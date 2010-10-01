# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms

### Change the Django's Users page

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User as UserModel

class __User(UserAdmin):
    list_display = ('username', 'group_list', 'last_name', 'first_name', 'email', 'is_staff', 'is_active')

    def group_list(self, obj):
        return ','.join(g.name for g in obj.groups.all())
    group_list.short_description = _(u'Groups')

admin.site.unregister(UserModel)
admin.site.register(UserModel, __User)

UserModel.description = _(u'Users of this system.')

### Rest of the models

from storage import models

class __Card(admin.ModelAdmin):
    def card_type(self, card):
        return card.__unicode__()

    list_display = ('card_type', 'client',
                    'state', 'discount', 'price', 'paid',
                    'count_available', 'count_sold', 'count_used',
                    'begin_date', 'end_date',
                    'is_active', 'reg_datetime', 'cancel_datetime')
    fieldsets = (
        (None, {'fields': ('card_ordinary', 'card_club', 'card_promo',
                           'client', 'discount', 'price', 'paid',
                           'count_available', 'count_sold', 'count_used',
                           'begin_date', 'end_date', 'is_active', 'cancel_datetime')}),
        )
admin.site.register(models.Card, __Card)

class __CardType(admin.ModelAdmin):

    def categories(self, cardtype):
        cats = cardtype.category.all()
        return u', '.join([unicode(i) for i in cats])

    def discounts(self, cardtype):
        discounts = cardtype.discount.all()
        return u', '.join([unicode(i) for i in discounts])

    filter_horizontal = ('category', 'discount')

class __CardOrdinary(__CardType):
    list_display = ('title', 'categories', 'discounts',
                    'is_priceless', 'is_active', 'reg_datetime')
    search_fields = ('title',)
admin.site.register(models.CardOrdinary, __CardOrdinary)

class __CardClub(__CardType):
    list_display = ('title', 'categories', 'discounts', 'price',
                    'count_days', 'is_active', 'reg_datetime')
    search_fields = ('title',)
admin.site.register(models.CardClub, __CardClub)

class __CardPromo(__CardType):
    list_display = ('title', 'categories', 'discounts', 'price',
                    'count_sold', 'count_days',
                    'date_activation', 'date_expiration',
                    'is_active', 'reg_datetime')
    search_fields = ('title',)
admin.site.register(models.CardPromo, __CardPromo)

class __PriceCategoryTeam(admin.ModelAdmin):
    list_display = ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active', 'reg_datetime')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active')}),)
admin.site.register(models.PriceCategoryTeam, __PriceCategoryTeam)

class __PriceCategoryRent(admin.ModelAdmin):
    list_display = ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active', 'reg_datetime')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active')}),)
admin.site.register(models.PriceCategoryRent, __PriceCategoryRent)

class __Discount(admin.ModelAdmin):
    list_display = ('title', 'percent', 'is_active', 'reg_datetime')
    ordering = ('percent', 'title')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'percent', 'is_active')}),)
admin.site.register(models.Discount, __Discount)

class __Room(admin.ModelAdmin):
    list_display = ('title', 'color', 'is_active', 'reg_datetime')
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'color', 'is_active')}),)
admin.site.register(models.Room, __Room)

class __DanceStyle(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'reg_datetime')
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'is_active')}),)
admin.site.register(models.DanceStyle, __DanceStyle)

class __Coach(admin.ModelAdmin):
    def name(self, user):
        return u'%s %s' % (user.last_name, user.first_name)
    name.short_description = _(u'Name')
    name.allow_tags = False

    list_display = ('name', 'phone', 'email', 'is_active', 'reg_datetime')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {
        'fields': ('last_name', 'first_name', 'phone', 'email',
                   'birth_date', 'desc', 'is_active')}),)
admin.site.register(models.Coach, __Coach)

class __Client(admin.ModelAdmin):
    def name(self, user):
        return u'%s %s' % (user.last_name, user.first_name)
    name.short_description = _(u'Name')
    name.allow_tags = False

    list_display = ('name', 'discount', 'rfid_code',
                    'phone', 'email', 'is_active', 'reg_datetime')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {
        'fields': ('last_name', 'first_name', 'phone', 'email',
                   'discount', 'birth_date', 'is_active')}),)
admin.site.register(models.Client, __Client)

class __Renter(admin.ModelAdmin):
    def name(self, user):
        return u'%s %s' % (user.last_name, user.first_name)
    name.short_description = _(u'Name')
    name.allow_tags = False

    list_display = ('name', 'phone', 'email', 'is_active', 'reg_datetime')
    search_fields = ('last_name', 'first_name')
    fieldsets = ((None, {
        'fields': ('last_name', 'first_name', 'phone', 'email',
                   'birth_date', 'desc', 'is_active')}),)
admin.site.register(models.Renter, __Renter)


### Interface for Team Model : Begin

class TeamInlineForm(forms.ModelForm):
    class Meta:
        model = models.Calendar
        exclude = ('rent')

class CalTeamItemInline(admin.TabularInline):
    model = models.Calendar
    form = TeamInlineForm
    extra = 1

class __Team(admin.ModelAdmin):
    def description(self, team):
        calendar_items = models.Calendar.objects.filter(team=team)
        cal_desc = u'<br>'.join([c.__unicode__() for c in calendar_items])
        return u'%s - %s - %s<hr/>%s' % (team.price_category,
                                         team.title,
                                         team.coach,
                                         cal_desc)
    description.short_description = _(u'Description')
    description.allow_tags = True

    list_display = ('description', 'dance_styles',
                    'duration', 'is_active', 'reg_datetime')
    ordering = ('price_category', 'title', 'coach')
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('price_category', 'dance_style', 'title',
                           'coach', 'duration', 'is_active')}),
        )
    inlines = [CalTeamItemInline]
admin.site.register(models.Team, __Team)

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

class __Rent(admin.ModelAdmin):
    list_display = ('price_category', 'title', 'renter', 'duration',
                    'paid', 'paid_status', 'is_active', 'reg_datetime')
    search_fields = ('renter', 'title')
    fieldsets = ((None, {
                    'fields': ('price_category', 'renter', 'paid', 'paid_status', 'is_active')}),
                 (_('Info'), {
                    'fields': ('title', 'duration', 'desc')}))
    inlines = [CalRentItemInline]
admin.site.register(models.Rent, __Rent)

### Interface for Rent Model : End

class __Calendar(admin.ModelAdmin):
    def description(self, item):
        return item.__unicode__()
    description.short_description = _(u'Description')
    description.allow_tags = False

    list_display = ('description', 'team', 'rent')
    ordering = ('day', 'time', 'room')
admin.site.register(models.Calendar, __Calendar)

class __Schedule(admin.ModelAdmin):
    list_display = ('room', 'begin_datetime', 'end_datetime',
                    'status', 'team', 'rent', 'change')
admin.site.register(models.Schedule, __Schedule)

class __Visit(admin.ModelAdmin):
    list_display = ('client', 'schedule', 'card')
admin.site.register(models.Visit, __Visit)

class __Log(admin.ModelAdmin):
    pass
admin.site.register(models.Log, __Log)
