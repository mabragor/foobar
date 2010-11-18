# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from datetime import timedelta, datetime, date

from django.conf import settings
from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from storage import translit

PAID_STATUS = ( ('0', _(u'Reserved')),
                ('1', _(u'Piad partially')),
                ('2', _(u'Paid')) )

class AbstractModel(models.Model):

    is_active = models.BooleanField(verbose_name=_(u'Is this record active?'), default=True)
    reg_datetime = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-is_active', '-reg_datetime')

    def __unicode__(self):
        return self.title

    def about(self, short=False, exclude_fields=tuple()):
        field_vals = {}

        for i in self._meta.fields:
            if i.name not in exclude_fields:
                internal_type = i.get_internal_type()
                value = getattr(self, i.name)
                if value is None:
                    field_vals.update( {i.name: None} )
                elif 'ForeignKey' == internal_type and hasattr(value, 'about'):
                    short = True
                    field_vals.update( {i.name: value.about(short)} )
                elif 'DateTimeField' == internal_type:
                    field_vals.update( {i.name: value.strftime('%Y-%m-%d %H:%M:%S')} )
                elif 'DateField' == internal_type:
                    field_vals.update( {i.name: value.strftime('%Y-%m-%d')} )
                elif 'TimeField' == internal_type:
                    field_vals.update( {i.name: value.strftime('%H:%M:%S')} )
                else:
                    field_vals.update( {i.name: value} )

        return field_vals

class PriceCategoryTeam(AbstractModel): # эконом, дисконт, эксклюзив, спецкурс...

    title = models.CharField(verbose_name=_('Title'), max_length=64)
    full_price = models.FloatField(verbose_name=_(u'Full price.'), default=0.00)
    half_price = models.FloatField(verbose_name=_(u'Half price.'), default=0.00)
    once_price = models.FloatField(verbose_name=_(u'One visit price.'), default=0.00)
    test_price = models.FloatField(verbose_name=_(u'Test price.'), default=0.00)

    class Meta:
        verbose_name = _(u'Price category of a team')
        verbose_name_plural = _(u'Price categories of a team')
        ordering = ('-is_active', '-full_price')

        #FIXME добавить привязку к набору скидок

class PriceCategoryRent(AbstractModel):

    title = models.CharField(verbose_name=_('Title'), max_length=64)
    full_price = models.FloatField(verbose_name=_(u'Full price.'), default=0.00)
    half_price = models.FloatField(verbose_name=_(u'Half price.'), default=0.00)
    once_price = models.FloatField(verbose_name=_(u'One visit price.'), default=0.00)
    test_price = models.FloatField(verbose_name=_(u'Test price.'), default=0.00)

    class Meta:

        verbose_name = _(u'Price category of a rent')
        verbose_name_plural = _(u'Price categories of a rent')

class Discount(AbstractModel):

    title = models.CharField(verbose_name=_('Title'), max_length=64)
    percent = models.IntegerField(verbose_name=_(u'The percent of a discount.'), default=0)

    class Meta:
        verbose_name = _(u'Discount')
        verbose_name_plural = _(u'Discounts')
        ordering = ('percent', 'title')

class AbstractCardType(AbstractModel): # флаер, пробное, разовое, абонемент, клубная карта, акция

    title = models.CharField(verbose_name=_('Title'), max_length=64,
                             help_text=_(u'The name of this item. It will show on the list of items.'))
    slug = models.SlugField(verbose_name=_('Slug'), max_length=128, help_text=_(u'ASCII name for this item.'))
    category = models.ManyToManyField(PriceCategoryTeam, verbose_name=_(u'Price category'))
    discount = models.ManyToManyField(Discount, verbose_name=_(u'Discount'))
    priority = models.IntegerField(verbose_name=_('Priority'), help_text=_(u'Priority for the algorithm to automatically select while the registration of a visit.'))

    class Meta:
        abstract = True
        ordering = ('-is_active', '-title')

    def about(self, short=False, exclude_fields=tuple()):
        result = super(AbstractCardType, self).about(short, exclude_fields)
        result.update( { 'price_categories': [i.about() for i in self.category.all() ],} )
        return result

class CardDuration(AbstractModel):
    """
    This model contains of the list:
      *  number of sold visits;
      *  number of days the card expires.
    """

    threshold = models.IntegerField(verbose_name=_(u'Threshold'),
                                    help_text=_(u'The threshold of applying a rule.'))
    value = models.IntegerField(verbose_name=_(u'Days.'),
                                help_text=_(u'The count days before expiration.'))

    class Meta:
        verbose_name = _(u'Duration')
        verbose_name_plural = _(u'Durations')

    def __unicode__(self):
        return 'Less or equal %(threshold)s then %(value)s' % {'threshold': self.threshold,
                                                               'value': self.value}

class CardOrdinary(AbstractCardType):

    is_priceless = models.BooleanField(verbose_name=_(u'Is priceless?'))
    use_threshold = models.BooleanField(verbose_name=_(u'Use threshold'),
                                        help_text=_(u'Use threshold to count an expiration date of the card?'),
                                        default=False)
    available_formula = models.CharField(verbose_name=_(u'Formula'), max_length=128, null=True, blank=True,
                                         help_text=_(u'Enter the formula to calculate available visits.'))

    class Meta:
        verbose_name = _(u'Ordinary card\'s type')
        verbose_name_plural = _(u'Ordinary card\'s types')

class CardClub(AbstractCardType): # 1day, 1month, 3m, 6m, 12m
    price = models.FloatField(verbose_name=_(u'Price.'), default=0.00)
    count_days = models.IntegerField(verbose_name=_(u'Duration in days.'))

    class Meta:
        verbose_name = _(u'Club card\'s type')
        verbose_name_plural = _(u'Club card\'s types')

class CardPromo(AbstractCardType):
    price = models.FloatField(verbose_name=_(u'Price.'), default=0.00)
    count_sold = models.IntegerField(verbose_name=_(u'Visits count.'))
    count_days = models.IntegerField(verbose_name=_(u'Duration in days.'))
    date_activation = models.DateField(verbose_name=_(u'Last date of an activation'), null=True, blank=True)
    date_expiration = models.DateField(verbose_name=_(u'Date of an expiration'), null=True, blank=True)

    class Meta:
        verbose_name = _(u'Promo card\'s type')
        verbose_name_plural = _(u'Promo card\'s types')

class AbstractUser(AbstractModel):

    last_name = models.CharField(verbose_name=_(u'Last name'), max_length=64)
    first_name = models.CharField(verbose_name=_(u'First name'), max_length=64)
    phone = models.CharField(verbose_name=_(u'Phone'), max_length=16)
    email = models.EmailField(verbose_name=_(u'E-mail'), max_length=64)
    birth_date = models.DateField(verbose_name=_(u'Birth date'))

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    def about(self, short=False, exclude_fields=tuple()):
        result = super(AbstractUser, self).about()
        result.update( { 'name': self.__unicode__(), } )
        return result

class Coach(AbstractUser):

    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')

    class Meta:
        verbose_name = _(u'Coach')
        verbose_name_plural = _(u'Coaches')

class Client(AbstractUser):

    rfid_code = models.CharField(verbose_name=_(u'RFID'), max_length=8, null=True, blank=True)
    discount = models.ForeignKey(Discount)

    class Meta:
        verbose_name = _(u'Client')
        verbose_name_plural = _(u'Clients')
        ordering = ('last_name', 'first_name')

    def about(self, short=False, exclude_fields=tuple()):
        result = super(Client, self).about()
        if not short:
            result.update( {'team_list': self.team_list()} )
        return result

    def team_list(self):
        short = True
        return [card.about(short) for card in self.card_set.all().order_by('-reg_datetime')]

class Renter(AbstractUser):

    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')

    class Meta:
        verbose_name = _(u'Renter')
        verbose_name_plural = _(u'Renters')

    def about(self, short=False, exclude_fields=tuple()):
        result = super(Renter, self).about()
        if not short:
            result.update( {'rent_list': self.rent_list()} )
        return result

    def rent_list(self):
        short = True
        return [rent.about(short) for rent in self.rent_set.all().order_by('-reg_datetime')]

class Card(AbstractModel):

    """
    This models contains of the records with a cards is bought by clients.
    """

    client = models.ForeignKey(Client, verbose_name=_(u'Client'))
    discount = models.ForeignKey(Discount)
    card_ordinary = models.ForeignKey(CardOrdinary, null=True, blank=True)
    card_club = models.ForeignKey(CardClub, null=True, blank=True)
    card_promo = models.ForeignKey(CardPromo, null=True, blank=True)
    price_category = models.ForeignKey(PriceCategoryTeam, verbose_name=_(u'Price category'), null=True, blank=True)
    price = models.FloatField(verbose_name=_(u'Price'), help_text=_(u'Price with all discounts.'), default=float(0.00))
    paid = models.FloatField(verbose_name=_(u'Paid'), help_text=_(u'Paid amount.'), default=float(0.00))
    count_sold = models.IntegerField(verbose_name=_(u'Exercises sold'))
    count_used = models.IntegerField(verbose_name=_(u'Exercises used'), default=0)
    count_available = models.IntegerField(verbose_name=_(u'Exercises available'), default=0)
    begin_date = models.DateField(verbose_name=_(u'Begin'), null=True)
    end_date = models.DateField(verbose_name=_(u'Expired'), null=True)
    cancel_datetime = models.DateTimeField(verbose_name=_(u'Cancelled'), null=True, blank=True)

    class Meta:
        verbose_name = _(u'Client\'s card')
        verbose_name_plural = _(u'Client\'s cards')

    def __unicode__(self):
        res = None
        if self.card_club is not None:
            res = _(u'Club')
        elif self.card_promo is not None:
            res = _(u'Promo')
        elif self.card_ordinary is not None:
            res = self.card_ordinary.__unicode__()
        else:
            res = _(u'Unknown')
        return unicode(res)

    @property
    def state(self):
        if self.begin_date is None:
            return _(u'Wait')
        if self.cancel_datetime is not None:
            return _(u'Cancel')
        if self.begin_date <= date.today() <= self.end_date:
            return _(u'Active')
        if self.end_date <= date.today():
            return _(u'Expired')

    def may_register(self):
        """
        This method checks the possibility to register a visit on the
        card.
        """
        return self.count_used < self.count_available

    def register_visit(self):
        """ This method registers a visit on the card."""
        print 'Register visit'

        # increment visits on client's card
        if self.count_available > self.count_used:
            self.count_used += 1
        else:
            raise RuntimeWarning(_(u'Check sources: %(avail)i and %(used)i') % {
                'avail': self.count_available,
                'used': self.count_used})

        # close card
        if self.count_available == self.count_used:
            print 'Cancel this card'
            self.cancel_datetime = datetime.now()

        # activate card (except promo)
        if self.begin_date is None or self.end_date is None:
            if self.card_ordinary or self.card_club:
                today = date.today()
                if self.card_ordinary:
                    card_title = _(u'Activate ordinary card')
                    # using the threshold
                    if self.card_ordinary.use_threshold:
                        queryset = CardDuration.objects.filter(threshold__gte=self.count_sold)
                        if len(queryset) > 0:
                            value = queryset[0].value
                            duration = timedelta(days=value)
                        else:
                            raise RuntimeWarning(_(u'Fill CardDuration model.'))
                    else:
                        duration = timedelta(days=30)
                else:
                    card_title = _(u'Activate club card')
                    duration = timetelta(days=self.card_club.count_days)
                self.begin_date = today
                self.end_date = today + duration
                #print u'%s [%s .. %s]' % (card_title, self.begin_date, self.end_date)

        self.save()

    @staticmethod
    def used_once(client, card):
        """
        Checks that ``client`` have used the ``card`` only once.

        ** Arguments **

        ``client`` is an instance of :model:`storage.models.Client`.

        ``card`` is instance of :model:`storage.models.CardOrdinary`.
        """
        qs = Card.objects.filter(client=client, card_ordinary=card, card_ordinary__slug=card.slug)
        return qs.count() > 0

class Room(AbstractModel):

    title = models.CharField(verbose_name=_(u'Title'), max_length=64,
                             help_text=_(u'Visible title for a room'))
    color = models.CharField(verbose_name=_(u'Color'), max_length=7,
                             help_text=_(u'HEX color, as #RRGGBB'))
    area = models.FloatField(verbose_name=_(u'Area'),
                             help_text=_(u'Room\'s area, in square meters'))
    flooring = models.CharField(verbose_name=_(u'Flooring'), max_length=200,
                                help_text=_(u'Flooring description, max 200 symbols'))

    class Meta:
        verbose_name = _(u'Room')
        verbose_name_plural = _(u'Rooms')

class DanceDirection(AbstractModel):

    title = models.CharField(verbose_name=_(u'Title'), max_length=64)

    class Meta:
        verbose_name = _(u'Direction')
        verbose_name_plural = _(u'Directions')

    def about(self, short=False, exclude_fields=tuple()):
        result = super(DanceDirection, self).about(short, exclude_fields)
        return result

class DanceStyle(AbstractModel):

    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    direction = models.ForeignKey(DanceDirection)

    class Meta:
        verbose_name = _(u'Style')
        verbose_name_plural = _(u'Styles')

    def about(self, short=False, exclude_fields=tuple()):
        result = super(DanceStyle, self).about(short, exclude_fields)
        result.update( { 'children': self.children(), } )
        return result

    def children(self):
        return [item.about() for item in self.team_set.all()]

class Team(AbstractModel):

    price_category = models.ForeignKey(PriceCategoryTeam)
    dance_style = models.ManyToManyField(DanceStyle, verbose_name=_(u'Dance style'))
    coaches = models.ManyToManyField(Coach, verbose_name=_(u'Coaches'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    duration = models.FloatField(verbose_name=_(u'Duration'), help_text=_(u'The duration of an event, in hours.'))

    class Meta:
        verbose_name = _(u'Team')
        verbose_name_plural = _(u'Teams')

    def about(self, short=False, exclude_fields=tuple()):
        exclude_fields = ('group',)
        result = super(Team, self).about(short, exclude_fields)
        result.update( {
            'dance_styles': self.dance_styles(),
            'coaches': u', '.join([unicode(a) for a in self.coaches.all()]),
            } )
        return result

    def dance_styles(self):
        return u', '.join([unicode(a) for a in self.dance_style.all()])

class Rent(AbstractModel):

    price_category = models.ForeignKey(PriceCategoryRent)
    renter = models.ForeignKey(Renter, verbose_name=_(u'Renter'))
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    desc = models.TextField(verbose_name=_(u'Description'), blank=True, default=u'')
    duration = models.FloatField(verbose_name=_(u'Duration'), help_text=_(u'The duration of an event.'))
    paid = models.FloatField(verbose_name=_(u'Paid amount'))
    paid_status = models.CharField(verbose_name=_(u'Paid status'), max_length=1, choices=PAID_STATUS, default=0)

    class Meta:
        verbose_name = _(u'Rent')
        verbose_name_plural = _(u'Rents')

class Calendar(AbstractModel):

    DAYS_OF_WEEK = ( ('0', _(u'Monday')),
                     ('1', _(u'Tuesday')),
                     ('2', _(u'Wednesday')),
                     ('3', _('Thursday')),
                     ('4', _(u'Friday')),
                     ('5', _(u'Saturday')),
                     ('6', _(u'Sunday')) )

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

    class Meta:
        verbose_name = _(u'Calendar')
        verbose_name_plural = _(u'Calendars')

    def __unicode__(self):
        return _(u'%(day)s at %(time)s in %(room)s') % {'day': self.get_day_display(),
                                                        'time': self.time,
                                                        'room': self.room}

    def about(self, short=False, exclude_fields=tuple()):
        exclude_fields = ('team', 'rent')
        result = super(Calendar, self).about(short, exclude_fields)
        if self.team is not None:
            result.update( self.team.about() )
            result.update( {'whatis': 'team'} )
        elif self.rent is not None:
            result.update( self.rent.about() )
            result.update( {'whatis': 'rent'} )
        return result


    def calc_end(self, begin, duration):
        return (datetime(1,1,1,begin.hour,begin.minute) \
                + timedelta(minutes=int(60 * duration)) \
                - timedelta(seconds=1)).time()

    def may_save(self):
        result = Calendar.objects.filter(room=self.room, day=self.day)

        # saving data
        event = self.team or self.rent
        e_begin = self.time
        e_end = self.calc_end(e_begin, event.duration)

        for item in result:
            obj = item.team or item.rent
            i_begin = item.time
            i_end = self.calc_end(i_begin, obj.duration)

            if (e_begin < i_end <= e_end) or \
                   (e_begin <= i_begin < e_end):
                return False

        return True

class Schedule(models.Model):

    EVENT_FIXED = ( ('0', _('Waiting')),
                    ('1', _('Done')),
                    ('2', _('Cancelled')) )

    coaches = models.ManyToManyField(Coach, verbose_name=_(u'Coaches'))
    team = models.ForeignKey(Team, verbose_name=_(u'Team'), null=True, blank=True)
    rent = models.ForeignKey(Rent, verbose_name=_(u'Rent'), null=True, blank=True)
    room = models.ForeignKey(Room, verbose_name=_(u'Room'))
    begin_datetime = models.DateTimeField(verbose_name=_(u'Begins'))
    end_datetime = models.DateTimeField(verbose_name=_(u'Ends'))
    status = models.CharField(verbose_name=_(u'Event status'), max_length=1, choices=EVENT_FIXED, default='0')

    class Meta:
        verbose_name = _(u'Schedule')
        verbose_name_plural = _(u'Schedules')

    def __unicode__(self):
        return u'%s(%s) %s' % (self.team, self.room, self.begin_datetime)

    def about(self, short=False, exclude_fields=tuple()):
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
            'status': self.status,
        }
        if self.team:
            obj.update( {'type': 'training',
                         'event': self.team.about(),
                         'coaches': [i.about() for i in self.coaches.all()]} )
        if self.rent:
            obj.update( {'type': 'rent', 'event': self.rent.about()} )
        return obj

    @property
    def is_team(self):
        return self.team is not None and self.rent is None

    @property
    def object(self):
        if self.is_team:
            return self.team
        else:
            return self.rent

    def get_visitors(self):
        return [(v.client.last_name,
                 v.client.first_name,
                 v.client.rfid_code,
                 v.reg_datetime) for v in self.visit_set.all()]

class Visit(AbstractModel): # FIXME models

    client = models.ForeignKey(Client)
    schedule = models.ForeignKey(Schedule, verbose_name=_(u'Event'))
    card = models.ForeignKey(Card, null=True, blank=True)

    class Meta:
        verbose_name = _(u'Visit')
        verbose_name_plural = _(u'Visits')
        unique_together = ('client', 'schedule')

    @property
    def title(self):
        return u'%s' % self.client

    def save(self):
        print 'Save visit'
        super(Visit, self).save()
        self.card.register_visit()

    # end of Visit model



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

    def about(self, short=False, exclude_fields=tuple()):
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

from logger.models import logging_postsave, logging_postdelete

for i in [Room, Client, Renter, Rent, Card, Calendar, Schedule, Visit]:
    models.signals.post_save.connect(logging_postsave, sender=i)
    models.signals.post_delete.connect(logging_postdelete, sender=i)
