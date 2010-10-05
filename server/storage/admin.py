# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms

from datetime import datetime, timedelta

### Change the Django's Users page

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User as UserModel, Group as GroupModel

class __User(UserAdmin):
    list_display = ('username', 'group_list', 'last_name', 'first_name', 'email', 'is_staff', 'is_active')

    def group_list(self, obj):
        return ','.join(g.name for g in obj.groups.all())
    group_list.short_description = _(u'Groups')

admin.site.unregister(UserModel)
admin.site.register(UserModel, __User)

UserModel.description = _(u'Users of this system.')
GroupModel.description = _(u'User groups of this system.')

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
models.Card.description = _(u'This model consists of records of training courses which clients ever had bought.')

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
models.CardOrdinary.description = _(u'This model consists of all possible types for ordinary cards.')

class __CardClub(__CardType):
    list_display = ('title', 'categories', 'discounts', 'price',
                    'count_days', 'is_active', 'reg_datetime')
    search_fields = ('title',)
admin.site.register(models.CardClub, __CardClub)
models.CardClub.description = _(u'This model consists of all possible types for club cards.')

class __CardPromo(__CardType):
    list_display = ('title', 'categories', 'discounts', 'price',
                    'count_sold', 'count_days',
                    'date_activation', 'date_expiration',
                    'is_active', 'reg_datetime')
    search_fields = ('title',)
admin.site.register(models.CardPromo, __CardPromo)
models.CardPromo.description = _(u'This model consists of all possible types for promo cards.')

class __PriceCategoryTeam(admin.ModelAdmin):
    list_display = ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active', 'reg_datetime')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active')}),)
admin.site.register(models.PriceCategoryTeam, __PriceCategoryTeam)
models.PriceCategoryTeam.description = _(u'This model consists of prices for every price category for teams.')

class __PriceCategoryRent(admin.ModelAdmin):
    list_display = ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active', 'reg_datetime')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'test_price', 'once_price', 'half_price', 'full_price', 'is_active')}),)
admin.site.register(models.PriceCategoryRent, __PriceCategoryRent)
models.PriceCategoryRent.description = _(u'This model consists of prices for every price category for rents.')

class __Discount(admin.ModelAdmin):
    list_display = ('title', 'percent', 'is_active', 'reg_datetime')
    ordering = ('percent', 'title')
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'percent', 'is_active')}),)
admin.site.register(models.Discount, __Discount)
models.Discount.description = _(u'This model consists of all possible discounts.')

### Interface for Room Model : Begin

class Room(admin.ModelAdmin):
    list_display = ('title', 'colored_field', 'area', 'flooring', 'is_active', 'reg_datetime')
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'color', 'area', 'flooring', 'is_active')}),)

    def colored_field(self, floor):
        return u'<div style="background-color: %s;">%s</div>' % (floor.color, floor.color)
    colored_field.short_description = _(u'Color')
    colored_field.allow_tags = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Method to change the default widget for color field. """
        from widgets import ColorPickerWidget
        if db_field.name == 'color':
            kwargs['widget'] = ColorPickerWidget
        return super(Room, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(models.Room, Room)
models.Room.description = _(u'This model consists of all available rooms.')

### Interface for Room Model : End

class __DanceStyle(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'reg_datetime')
    ordering = ('title', )
    search_fields = ('title',)
    fieldsets = ((None, {'fields': ('title', 'is_active')}),)
admin.site.register(models.DanceStyle, __DanceStyle)
models.DanceStyle.description = _(u'This model consists of all available dance styles.')

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
models.Coach.description = _(u'This model consists of all available coaches.')

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
models.Client.description = _(u'This model consists of all registered clients.')

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
models.Renter.description = _(u'This model consists of all registered renters.')


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
        return u'%s - %s<hr/>%s<hr/>%s' % (team.price_category,
                                           team.title,
                                           ','.join([c.__unicode__() for c in team.coaches.all()]),
                                           cal_desc)
    description.short_description = _(u'Description')
    description.allow_tags = True

    list_display = ('description', 'dance_styles',
                    'duration', 'is_active', 'reg_datetime')
    ordering = ('price_category', 'title', 'coaches')
    search_fields = ('title',)
    fieldsets = (
        (None, {'fields': ('price_category', 'dance_style', 'title',
                           'coaches', 'duration', 'is_active')}),
        )
    inlines = [CalTeamItemInline]
admin.site.register(models.Team, __Team)
models.Team.description = _(u'This model consists of all available teams.')

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
models.Rent.description = _(u'This model consists of all available rents.')

### Interface for Rent Model : End

### Interface for Calendar Model : Begin

class CalendarForm(forms.ModelForm):

    class Meta:
        model = models.Calendar

    def event_obj(self, o_desc):
        if type(o_desc) is dict:
            team = o_desc['team']
            rent = o_desc['rent']
        else:
            team = o_desc.team
            rent = o_desc.rent
        return team or rent

    def calc_end(self, begin, duration):
        return (datetime(1,1,1,begin.hour,begin.minute) \
                + timedelta(minutes=int(60 * duration)) \
                - timedelta(seconds=1)).time()

    def clean(self):
        d = self.cleaned_data

        if d['team'] is None and d['rent'] is None:
            raise forms.ValidationError(_(u'What event will happen?'))

        result = models.Calendar.objects.filter(room=d['room'], day=d['day'])

        # saving data
        event = self.event_obj(d)
        e_begin = d['time']
        e_end = self.calc_end(e_begin, event.duration)

        for item in result:
            obj = self.event_obj(item)
            i_begin = item.time
            i_end = self.calc_end(i_begin, obj.duration)

            if (e_begin < i_end <= e_end) or \
                   (e_begin <= i_begin < e_end):
                raise forms.ValidationError(_(u'Impossible to place this event!'))

        return self.cleaned_data

class __Calendar(admin.ModelAdmin):
    list_display = ('description', 'team', 'rent')
    ordering = ('day', 'time', 'room')
    form = CalendarForm

    def description(self, item):
        return item.__unicode__()
    description.short_description = _(u'Description')
    description.allow_tags = False

admin.site.register(models.Calendar, __Calendar)
models.Calendar.description = _(u'This model consists of records with events (team or rent) which assigned on a week.')

### Interface for Calendar Model : End

class __Schedule(admin.ModelAdmin):
    list_display = ('room', 'begin_datetime', 'end_datetime',
                    'status', 'team', 'rent', 'change')
admin.site.register(models.Schedule, __Schedule)
models.Schedule.description = _(u'This model consists of records with scheduled events (team or rent).')

class __Visit(admin.ModelAdmin):
    list_display = ('client', 'schedule', 'card')
admin.site.register(models.Visit, __Visit)
models.Visit.description = _(u'This model consists of all registered visits of trainings.')
