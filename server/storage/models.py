# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

PAID_STATUS = enumerate( (_(u'Reserved'),
                          _(u'Piad partially'),
                          _(u'Paid')) )

class AbstractUser(models.Model):

    last_name = models.CharField(verbose_name=_(u'Last name'), max_length=64)
    first_name = models.CharField(verbose_name=_(u'First name'), max_length=64)
    phone = models.CharField(verbose_name=_(u'Phone'), max_length=16)
    email = models.EmailField(verbose_name=_(u'E-mail'), max_length=64, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_(u'Birth date'))
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def about(self):
        return {
            'id': self.pk,
            'name': '%s %s' % (self.last_name, self.first_name),
            'last_name': self.last_name,
            'first_name': self.first_name,
            'phone': self.phone,
            'email': self.email,
            'birth_date': self.birth_date,
            }

class Coach(AbstractUser):
    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')

    class Meta:
        verbose_name = _(u'Coach')
        verbose_name_plural = _(u'Coaches')

    def about(self):
        result = super(Coach, self).about()
        result.update( {
                'desc': self.desc,
                } )
        return result

class Client(AbstractUser):

    DISCOUNT = enumerate( (_(u'No discount'),
                           _(u'Exists'),) )

    rfid_code = models.CharField(verbose_name=_(u'RFID'), max_length=8)
    discount = models.CharField(verbose_name=_(u'Discount'), max_length=1,
                                choices=DISCOUNT, default=0)

    class Meta:
        verbose_name = _(u'Client')
        verbose_name_plural = _(u'Clients')

    def about(self, short=False):
        result = super(Client, self).about()
        result.update( {
                'rfid_code': self.rfid_code,
                'discount': self.discount,
                } )
        if not short:
            result.update( {'team_list': self.team_list()} )
        return result

    def team_list(self):
        return [card.about(True) for card in self.card_set.all().order_by('-reg_datetime')]

class Renter(AbstractUser):

    phone_mobile = models.CharField(verbose_name=_(u'Mobile phone'), max_length=16, blank=True, null=True)
    phone_work = models.CharField(verbose_name=_(u'Work phone'), max_length=16, blank=True, null=True)
    phone_home = models.CharField(verbose_name=_(u'Home phone'), max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _(u'Renter')
        verbose_name_plural = _(u'Renters')

    def about(self, short=False):
        result = super(Renter, self).about()
        result.update( {
                'phone_mobile': self.phone_mobile,
                'phone_work': self.phone_work,
                'phone_home': self.phone_home,
                } )
        if not short:
            result.update( {'rent_list': self.rent_list()} )
        return result

    def rent_list(self):
        return [rent.about(True) for rent in self.rent_set.all().order_by('-reg_date')]

class Rent(models.Model):


    renter = models.ForeignKey(Renter, verbose_name=_(u'Renter'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')
    duration = models.FloatField(verbose_name=_(u'Duration'), help_text=_(u'The duration of an event.'))
    paid = models.FloatField(verbose_name=_(u'Paid amount'))
    paid_status = models.CharField(verbose_name=_(u'Paid status'), max_length=1, choices=PAID_STATUS, default=0)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Rent')
        verbose_name_plural = _(u'Rents')

    def __unicode__(self):
        return self.title

    def about(self, short=False):
        result = {
            'id': self.pk,
            'renter': self.renter.about(short),
            'title': self.title,
            'desc': self.desc,
            'duration': self.duration,
            'paid': self.paid,
            'paid_status': self.paid_status,
            'reg_date': self.reg_date,
            }
        return result

class Room(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    color = models.CharField(verbose_name=_(u'Color'), max_length=6)

    class Meta:
        verbose_name = _(u'Room')
        verbose_name_plural = _(u'Rooms')

    def __unicode__(self):
        return self.title

    def about(self):
        return {
            'id': self.pk,
            'title': self.title,
            'color': self.color,
        }

class Group(models.Model):

    title = models.CharField(verbose_name=_(u'Title'), max_length=64)

    class Meta:
        verbose_name = _(u'Style')
        verbose_name_plural = _(u'Styles')

    def __unicode__(self):
        return self.title

    def about(self):
        return {
            'id': self.pk,
            'title': self.title,
            'children': self.children,
            }

    @property
    def children(self):
        return [item.about() for item in self.team_set.all()]

PRICE_CATEGORY = enumerate( (_(u'Normal'), _(u'High')) )

class Price(models.Model):
    title = models.CharField(max_length=64)
    cost = models.FloatField()
    count = models.IntegerField()
    discount = models.IntegerField()
    price_category = models.CharField(verbose_name=_(u'Price category'), max_length=1, choices=PRICE_CATEGORY, default=0)
    special = models.BooleanField(verbose_name=_(u'Is this a special record?'))

    class Meta:
        verbose_name = _(u'Price')
        verbose_name_plural = _(u'Prices')

    def __unicode__(self):
        return self.title

class Team(models.Model):

    group = models.ManyToManyField(Group, verbose_name=_(u'Group'))
    coach = models.ForeignKey(Coach, verbose_name=_(u'Coach'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    duration = models.FloatField(verbose_name=_(u'Duration'), help_text=_(u'The duration of an event.'))
    price_category = models.CharField(verbose_name=_(u'Price category'), max_length=1, choices=PRICE_CATEGORY, default=0)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Team')
        verbose_name_plural = _(u'Teams')

    def __unicode__(self):
        return self.title

    def groups(self):
        return ','.join([unicode(a) for a in self.group.all()])

    def price(self):
        return Price.objects.filter(price_category=self.price_category)

    def about(self):
        return {
            'id': self.pk,
            'groups': self.groups(),
            'coach': self.coach.about(),
            'title': self.title,
            'duration': self.duration,
            'price_category': self.price_category,
            }

class Calendar(models.Model):

    DAYS_OF_WEEK = enumerate( (_(u'Monday'), _(u'Tuesday'),
                               _(u'Wednesday'), _('Thursday'),
                               _(u'Friday'), _(u'Saturday'),
                               _(u'Sunday')) )

    team = models.ForeignKey(Team, verbose_name=_(u'Team'),
                             null=True, blank=True)
    rent = models.ForeignKey(Rent, verbose_name=_(u'Rent'),
                             null=True, blank=True)
    room = models.ForeignKey(Room, verbose_name=_(u'Room'))
    time = models.TimeField(verbose_name=_(u'Time'),
                            help_text=_(u'Time of the event'))
    day = models.CharField(verbose_name=_(u'Week day'),
                           help_text=_(u'The day of a week.'),
                           max_length=1, choices=DAYS_OF_WEEK,
                           default=0)

    def __unicode__(self):
        return _(u'%s at %s in %s') % (self.get_day_display(), self.time, self.room)

    def about(self):
        result = {
            'room': self.room.about(),
            'time': self.time,
            'day': self.day,
            }
        if self.team is not None:
            result.update( self.team.about() )
            result.update( {'whatis': 'team'} )
        elif self.rent is not None:
            result.update( self.rent.about() )
            result.update( {'whatis': 'rent'} )
        return result

class Card(models.Model):

    CARD_TYPE = enumerate( (_(u'Normal card'), _(u'Club card')) )
    CARD_STATE = enumerate( (_(u'Wait'), _(u'Active'), _(u'Expired'), _(u'Used'), _(u'Cancel')) )

    team = models.ForeignKey(Team, verbose_name=_(u'Team'))
    client = models.ForeignKey(Client, verbose_name=_(u'Client'))
    card_type = models.CharField(verbose_name=_(u'Type'), help_text=_(u'Type of client\'s card'), max_length=1, choices=CARD_TYPE, default=0)
    state = models.CharField(verbose_name=_(u'State'), help_text=_(u'State of record'), max_length=1, choices=CARD_STATE, default=0)
    begin_date = models.DateField(verbose_name=_(u'Begin'), null=True)
    end_date = models.DateField(verbose_name=_(u'Expired'), null=True)
    duration = models.IntegerField(default=0)
    count_sold = models.IntegerField(verbose_name=_(u'Exercises sold'))
    count_used = models.IntegerField(verbose_name=_(u'Exercises used'), default=0)
    price = models.FloatField(verbose_name=_(u'Price'), help_text=_(u'Price.'), default=float(0.00))
    paid = models.FloatField(verbose_name=_(u'Paid'), help_text=_(u'Paid amount.'), default=float(0.00))
    paid_status = models.CharField(verbose_name=_(u'Paid status'), max_length=1, choices=PAID_STATUS, default=0)
    reg_datetime = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    cancel_datetime = models.DateTimeField(verbose_name=_(u'Registered'), null=True)

    class Meta:
        verbose_name = _(u'Card')
        verbose_name_plural = _(u'Card')
        ordering = ['-reg_date']

    def __unicode__(self):
        return self.team.title

    def about(self, short=False):
        obj = {
            'id': self.pk,
            'team': self.team.about(),
            'card_type': self.card_type,
            'state': self.state,
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'duration': self.duration,
            'count_sold': self.count_sold,
            'count_used': self.count_used,
            'price': self.price,
            'paid': self.paid,
            'paid_status': self.paid_status,
            'reg_datetime': self.reg_datetime,
            'cancel_datetime': self.cancel_datetime,
            }
        if not short:
            obj.update( {'client': self.client.about(),} )
        return obj

class Schedule(models.Model):

    EVENT_FIXED = enumerate( (_('Waiting'), _('Done'), _('Cancelled')) )

    change = models.ForeignKey(Coach, verbose_name=_(u'Change'), null=True, blank=True)
    team = models.ForeignKey(Team, verbose_name=_(u'Team'), null=True, blank=True)
    rent = models.ForeignKey(Rent, verbose_name=_(u'Rent'), null=True, blank=True)
    room = models.ForeignKey(Room, verbose_name=_(u'Room'))
    begin_datetime = models.DateTimeField(verbose_name=_(u'Begins'))
    end_datetime = models.DateTimeField(verbose_name=_(u'Ends'))
    event_fixed = models.CharField(verbose_name=_(u'Event fixed'), max_length=1, choices=EVENT_FIXED, default='0')

    class Meta:
        verbose_name = _(u'Schedule')
        verbose_name_plural = _(u'Schedules')

    def __unicode__(self):
        return u'%s(%s) %s' % (self.team, self.room, self.begin_datetime)

    def about(self):
        now = datetime.now()
        if self.begin_datetime + timedelta(minutes=15) < now:
            status = 2 # passed
        elif now > self.begin_datetime:
            status = 1 # warning
        else:
            status = 0 # waiting
        obj = {
            'id': self.pk,
            'room': self.room.about(),
            'begin_datetime': self.begin_datetime,
            'end_datetime': self.end_datetime,
            'event_fixed': self.event_fixed,
        }
        if self.team:
            obj.update( {'type': 'training',
                         'event': self.team.about()} )
            if self.change is not None:
                obj.update( {'change': self.change.pk} )
        if self.rent:
            obj.update( {'type': 'rent', 'event': self.rent.about()} )
        return obj

    @property
    def typeof(self):
        if self.team is None:
            return 1
        else:
            return 0

    @property
    def object(self):
        if self.team is not None:
            return self.team
        else:
            return self.rent

    def get_visitors(self):
        return [(v.client.last_name,
                 v.client.first_name,
                 v.client.rfid_code) for v in self.visit_set.all()]

class Visit(models.Model):

    client = models.ForeignKey(Client, verbose_name=_(u'Client'))
    schedule = models.ForeignKey(Schedule, verbose_name=_(u'Event'))
    card = models.ForeignKey(Card, verbose_name=_(u'Card'), null=True, blank=True)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Visit')
        verbose_name_plural = _(u'Visits')
        unique_together = ('client', 'schedule')

    def about(self):
        return {
            'id': self.pk,
            'client': self.client.about(),
            'event': self.schedule.about(),
            'card': self.card.about(),
            'reg_date': self.reg_date,
            }

TYPICAL_CHARGES = (
    ('0', _('Coach change')),
    ('1', _('Economic expenses')),
    ('2', _('Salary')),
    ('3', _('Subsist')),
    ('4', _('Advertising')),
    ('5', _('Capital investments')),
    )

TYPICAL_GAIN = (
    ('0', _('Basic services')),
    ('1', _('Club cards')),
    ('2', _('Gift certificates')),
    ('3', _('Open abonement')),
    ('4', _('ISIC cards')),
    ('5', _('Cofe machine')),
    ('6', _('Room rent')),
    ('7', _('Dance show')),
    )

# Учёт средств

RFIDCARDS = '0'
TYPE_STATUS = ((RFIDCARDS, _(u'RFID cards')), ('1', _(u'Unknown')),)

class Accounting(models.Model):

    id = models.CharField(verbose_name=_(u'Type'), max_length=4, choices=TYPE_STATUS, primary_key=True)
    count = models.IntegerField(verbose_name=_(u'Count'), default=0)

    class Meta:
        verbose_name = _(u'Accounting')
        verbose_name_plural = _(u'Accountings')

    def __unicode__(self):
        return '%s %i' % (self.get_id_display(), self.count)

    def add(self, count):
        self.count += count
        self.save()

    def sub(self, count):
        if self.count < count:
            print self.count, count
            raise RuntimeWarning
        self.count -= count
        self.save()

    def about(self):
        return {
            'id': self.id,
            'type': self.get_id_display(),
            'count': self.count,
            }

class Flow(models.Model):

    INFLOW = '0'
    OUTFLOW = '1'
    FLOW_STATUS = ((INFLOW, _(u'Inflow')), (OUTFLOW, _(u'Outflow')),)

    user = models.ForeignKey(User, verbose_name=_(u'User'))
    action = models.CharField(verbose_name=_(u'Action'), max_length=1, choices=FLOW_STATUS)
    type = models.CharField(verbose_name=_(u'Type'), max_length=4, choices=TYPE_STATUS)
    count = models.IntegerField(verbose_name=_(u'Count'))
    price = models.FloatField(verbose_name=_(u'Price'), default=float(0.00))
    total = models.FloatField(verbose_name=_(u'Total'), default=float(0.00))
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Flow')
        verbose_name_plural = _(u'Flows')

    def __unicode__(self):
        return '%s %s %s %f' % (self.user,
                                self.get_action_display(),
                                self.get_type_display(),
                                self.total)

    def save(self):
        super(Flow, self).save()
        accounting, created = Accounting.objects.get_or_create(id=self.type)
        if self.action == self.INFLOW:
            accounting.add(self.count)
        elif self.action == self.OUTFLOW:
            accounting.sub(self.count)
        else:
            raise RuntimeWarning('Action is %i.' % self.action)

# Журналирование

class Log(models.Model):

    user = models.ForeignKey(User, verbose_name=_(u'User'), null=True, blank=True)
    action = models.CharField(verbose_name=_(u'Action'), max_length=64)
    model = models.CharField(verbose_name=_('Model'), max_length=256)
    data = models.TextField(verbose_name=_('Data'))
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Log')
        verbose_name_plural = _(u'Logs')

    def __unicode__(self):
        return '%s %s' % (self.model, self.action)

def logging_abstract(instance, action, **kwargs):
    from django.utils import simplejson
    from lib import DatetimeJSONEncoderQt
    json = simplejson.dumps(instance.__dict__, cls=DatetimeJSONEncoderQt)
    log = Log(model=instance, data=json, action=action)
    log.save()

def logging_postsave(instance, created, **kwargs):
    logging_abstract(instance, created and 'create' or 'update', **kwargs)

def logging_postdelete(instance, **kwargs):
    logging_abstract(instance, 'delete', **kwargs)

for i in [Client, Renter, Rent, Room, Group, Team, Card,
          Schedule, Visit]:
    models.signals.post_save.connect(logging_postsave, sender=i)
    models.signals.post_delete.connect(logging_postdelete, sender=i)

def logging_mysignals(sender, **kwargs):
    log = Log(user=sender, model='global action',
              data='', action=kwargs['action'])
    log.save()

from signals import signal_log_action
signal_log_action.connect(logging_mysignals)
