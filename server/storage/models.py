# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime
from django.conf import settings

class AbstractUser(models.Model):
    last_name = models.CharField(verbose_name=_(u'Last name'), max_length=64)
    first_name = models.CharField(verbose_name=_(u'First name'), max_length=64)
    email = models.EmailField(verbose_name=_(u'E-mail'), max_length=64, blank=True, null=True)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def about(self):
        return {
            'id': self.pk,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'email': self.email,
            }

class Coach(AbstractUser):

    class Meta:
        verbose_name = _(u'Coach')
        verbose_name_plural = _(u'Coaches')

    def about(self):
        result = super(Coach, self).about()
        #result.update( {} )
        return result

class Client(AbstractUser):
    rfid_code = models.CharField(verbose_name=_(u'RFID'), max_length=8)

    class Meta:
        verbose_name = _(u'Client')
        verbose_name_plural = _(u'Clients')

    def about(self, short=False):
        result = super(Client, self).about()
        result.update( {'rfid_code': self.rfid_code} )
        if not short:
            result.update( {'team_list': self.team_list()} )
        return result

    def team_list(self):
        return [card.about(True) for card in self.card_set.all().order_by('-reg_date')]

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
    RENT_STATUS = (('0', _(u'Reserved')), ('1', _(u'Piad partially')), ('2', _('Paid')))
    renter = models.ForeignKey(Renter, verbose_name=_(u'Renter'))
    status = models.CharField(verbose_name=_(u'Status'), max_length=1, choices=RENT_STATUS, default=0)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    begin_date = models.DateField(verbose_name=_(u'Begin'))
    end_date = models.DateField(verbose_name=_(u'End'))
    paid = models.FloatField(verbose_name=_(u'Paid amount'))

    class Meta:
        verbose_name = _(u'Rent')
        verbose_name_plural = _(u'Rents')

    def __unicode__(self):
        return self.title

    def about(self, short=False):
        result = {
            'id': self.pk,
            'status': self.status,
            'title': self.title,
            'desc': self.desc,
            'reg_date': self.reg_date,
            'begin_date': self.begin_date,
            'end_date': self.end_date,
            'paid': self.paid,
            'renter': self.renter.about(short),
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

class Team(models.Model):
    group = models.ManyToManyField(Group, verbose_name=_(u'Group'))
    coach = models.ForeignKey(Coach, verbose_name=_(u'Coach'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    duration = models.FloatField(verbose_name=_(u'Duration'))
    count = models.IntegerField(verbose_name=_(u'Count'))
    price = models.FloatField(verbose_name=_(u'Price'),
                              help_text=_(u'The price of this team.'),
                              default=float(0.00))
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    salary = models.IntegerField(verbose_name=_(u'Salary'),
                                 help_text=_(u'The salary for this team.'),
                                 default=0)

    class Meta:
        verbose_name = _(u'Team')
        verbose_name_plural = _(u'Teams')

    def __unicode__(self):
        return self.title

    def groups(self):
        return ','.join([unicode(a) for a in self.group.all()])

    def about(self):
        return {
            'id': self.pk,
            'groups': self.groups(),
            'coach': self.coach,
            'title': self.title,
            'duration': self.duration,
            'count': self.count,
            'price': self.price,
            }

class Card(models.Model):
    CARD_TYPE = (('0', _(u'Normal card')), ('1', _(u'Club card')))
    team = models.ForeignKey(Team, verbose_name=_(u'Team'))
    client = models.ForeignKey(Client, verbose_name=_(u'Client'))
    type = models.CharField(verbose_name=_(u'Type'),
                            help_text=_(u'Type of client\'s card'),
                            max_length=1, choices=CARD_TYPE,
                            default=0)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    bgn_date = models.DateTimeField(verbose_name=_(u'Begin'))
    exp_date = models.DateTimeField(verbose_name=_(u'Expired'))
    cnl_date = models.DateTimeField(verbose_name=_(u'Cancelled'), null=True)
    count_sold = models.IntegerField(verbose_name=_(u'Exercises sold'))
    count_used = models.IntegerField(verbose_name=_(u'Exercises used'), default=0)
    price = models.FloatField(verbose_name=_(u'Price'),
                              help_text=_(u'The price of this team.'),
                              default=float(0.00))

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
            'type': self.type,
            'register': self.reg_date,
            'begin': self.bgn_date,
            'expire': self.exp_date,
            'cancel': self.cnl_date,
            'sold': self.count_sold,
            'used': self.count_used,
            'price': self.price,
            }
        if not short:
            obj.update( {'client': self.client.about(),} )
        return obj

    def deleteable(self):
        #if self.reg_date <= datetime.now() - timedelta(days=1):
        #    return False
        if self.is_old():
            return False
        if self.action_set.count():
            return False
        return True

    def is_old(self):
        return self.exp_date < datetime.now()

class Schedule(models.Model):
    ACTION_STATUSES = (
        ('0', _('Waiting')),
        ('1', _('Warning')),
        ('2', _('Passed')),
    )
    room = models.ForeignKey(Room, verbose_name=_(u'Room'))
    team = models.ForeignKey(Team, verbose_name=_(u'Team'), null=True, blank=True)
    rent = models.ForeignKey(Rent, verbose_name=_(u'Rent'), null=True, blank=True)
    begin = models.DateTimeField(verbose_name=_(u'Begins'))
    end = models.DateTimeField(verbose_name=_(u'Ends'))
    duration = models.FloatField(verbose_name=_(u'Duration'))
    status = models.CharField(verbose_name=_(u'Status'), max_length=1, choices=ACTION_STATUSES, null=True)
    change = models.ForeignKey(Coach, verbose_name=_(u'Change'), null=True, blank=True)
    # НЕ НУЖНО
    looking = models.BooleanField(verbose_name=_(u'Is looking for members?'), default=True)
    places = models.BooleanField(verbose_name=_(u'Are there free places?'), default=True)

    class Meta:
        verbose_name = _(u'Schedule')
        verbose_name_plural = _(u'Schedules')

    def __unicode__(self):
        return u'%s(%s) %s' % (self.team, self.room, self.begin)

    def about(self):
        obj = {
            'id': self.pk,
            'room': self.room.about(),
            'begin': self.begin,
            'end': self.end,
            'status': self.status,
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

    def get_for_user(self, user):
        type = None
        if user is None or self.end < datetime.today():
            type = 'unavailable'
        else:
            cards = Card.objects.filter(client=user, team=self.team, exp_date__gt=datetime.today())
            for item in cards:
                if item.count > 0:
                    type = 'available'
        if type is None:
            type = 'posible'

        obj = {
            'id': self.pk,
            'title': self.team.__unicode__(),
            'room': self.room.__unicode__(),
            'start': self.begin.strftime('%H:%M'),
            'end': self.end.strftime('%H:%M'),
            'coach': ' '.join([str(item) for item in self.team.coach.all()]),
            'type': type
        }
        return obj

    @classmethod
    def get_unstatus_event(self):
        d = datetime.now() - timedelta(minutes=settings.CHECK_STATUS_INTERVAL)
        try:
            event = self._default_manager.filter(begin__lte=d, status__isnull=True)[0:1].get()
            return {
                'id': event.pk,
                'title': '%s - %s' % (event.team.__unicode__(), event.room.__unicode__()),
                'date': '%s - %s' % (event.begin, event.end)
            }
        except self.DoesNotExist:
            return None

    def get_visitors(self):
        return [(v.client.last_name,
                 v.client.first_name,
                 v.client.rfid_code) for v in self.visit_set.all()]

class Visit(models.Model):
    client = models.ForeignKey(Client, verbose_name=_(u'Client'))
    schedule = models.ForeignKey(Schedule, verbose_name=_(u'Event'))
    card = models.ForeignKey(Card, verbose_name=_(u'Card'), null=True, blank=True)
    when = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

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
            'when': self.when,
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

