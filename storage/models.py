# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime
from django.conf import settings

class AbstractUser(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, blank=True, null=True)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode('%s %s' % (self.first_name, self.last_name))

class Coach(AbstractUser):

    class Meta:
        verbose_name = _(u'Coach')
        verbose_name_plural = _(u'Coaches')

    def get_store_obj(self):
        obj = {
            'id': self.pk,
            'name': self.__unicode__()
        }
        return obj

class Client(AbstractUser):
    rfid_code = models.CharField(max_length=8)

    class Meta:
        verbose_name = _(u'Client')
        verbose_name_plural = _(u'Clients')

    def get_course_list(self):
        return [card.get_info() for card in self.card_set.all().order_by('-reg_date')]

class Renter(AbstractUser):
    phone_mobile = models.CharField(max_length=16, blank=True, null=True)
    phone_work = models.CharField(max_length=16, blank=True, null=True)
    phone_home = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _(u'Renter')
        verbose_name_plural = _(u'Renters')

class Room(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    color = models.CharField(verbose_name=_(u'Color'), max_length=6)

    class Meta:
        verbose_name = _(u'Room')
        verbose_name_plural = _(u'Rooms')

    def __unicode__(self):
        return self.title

    def get_store_obj(self):
        obj = {
            'id': self.pk,
            'color': self.color,
            'text': self.title
        }
        return obj

    def get_tree_node(self):
        obj = {
            'id': self.pk,
            'text': self.title,
            'leaf': True,
            'cls': 'file',
            'color': self.color
        }
        return obj

class Group(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)

    class Meta:
        verbose_name = _(u'Style')
        verbose_name_plural = _(u'Styles')

    def __unicode__(self):
        return self.title

    def get_tree_node(self):
        obj = {
            'id': 'g_%s' % self.pk,
            'text': self.title,
            'cls': 'folder',
            'children': [item.get_tree_node() for item in self.course_set.all()],
            'allowDrag': False
        }
        return obj

    def get_node(self):
        return {
            'id': self.pk,
            'title': self.title,
            'children': [item.get_node() for item in self.course_set.all()]
            }

class Rent(models.Model):
    RENT_STATUS = (('0', _(u'Unpaid')), ('1', _(u'Partially')), ('2', _('Paid')))
    renter = models.ForeignKey(Renter)
    status = models.CharField(max_length=1, choices=RENT_STATUS, default=0)
    title = models.CharField(max_length=64)
    desc = models.TextField(blank=True, default=u'')
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    begin_date = models.DateTimeField(verbose_name=_(u'Begin'))
    end_date = models.DateTimeField(verbose_name=_(u'End'))
    paid = models.FloatField()

    class Meta:
        verbose_name = _(u'Rent')
        verbose_name_plural = _(u'Rents')

    def __unicode__(self):
        return self.title

class Course(models.Model):
    group = models.ManyToManyField(Group)
    coach = models.ManyToManyField(Coach)
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    duration = models.FloatField()
    count = models.IntegerField(verbose_name=_(u'Count'))
    price = models.FloatField(verbose_name=_(u'Price'),
                              help_text=_(u'The price of the course.'),
                              default=float(0.00))
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    salary = models.IntegerField(verbose_name=_(u'Salary'),
                                 help_text=_(u'The salary for the course.'),
                                 default=0)

    class Meta:
        verbose_name = _(u'Course')
        verbose_name_plural = _(u'Courses')

    def __unicode__(self):
        return self.title

    def coaches(self):
        return ','.join([unicode(a) for a in self.coach.all()])

    def groups(self):
        return ','.join([unicode(a) for a in self.group.all()])

    def get_tree_node(self):
        coaches = ', '.join(unicode(coach) for coach in self.coach.all())
        return {
            'id': self.pk,
            'text': '%s : %s' % (self.title, coaches),
            'leaf': True,
            'cls': 'file'
            }

    def get_node(self):
        return {
            'id': self.pk,
            'title': self.title,
            'coaches': ','.join([item.__unicode__() for item in self.coach.all()]),
            'count': self.count,
            'price': self.price,
            'duration': self.duration
            }

class Card(models.Model):
    CARD_TYPE = (('0', _(u'Normal card')), ('1', _(u'Club card')))
    course = models.ForeignKey(Course)
    client = models.ForeignKey(Client)
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
                              help_text=_(u'The price of the course.'),
                              default=float(0.00))

    class Meta:
        verbose_name = _(u'Card')
        verbose_name_plural = _(u'Card')
        ordering = ['-reg_date']

    def __unicode__(self):
        return self.course.title

    def get_info(self):
        return {
            'id': self.pk,
            'course_id': self.course.pk,
            'title': self.course.title,
            'reg_date': self.reg_date,
            'bgn_date': self.bgn_date,
            'exp_date': self.exp_date,
            'cnl_date': self.cnl_date,
            'count_sold': self.count_sold,
            'count_used': self.count_used,
            'price': self.price,
            'card_type': self.type,
            # это надо будет удалить
            'deleteable': False,#self.deleteable(),
            'is_old': self.is_old()
        }

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
        ('1', _('Done')),
        ('2', _('Cancelled')),
    )
    room = models.ForeignKey(Room)
    course = models.ForeignKey(Course, null=True, blank=True)
    rent = models.ForeignKey(Rent, null=True, blank=True)
    begin = models.DateTimeField(verbose_name=_(u'Begins'))
    # НЕ НУЖНО
    looking = models.BooleanField(verbose_name=_(u'Is looking for members?'), default=True)
    # НЕ НУЖНО
    places = models.BooleanField(verbose_name=_(u'Are there free places?'), default=True)
    status = models.CharField(verbose_name=_(u'Status'), max_length=1, choices=ACTION_STATUSES, null=True)
    change = models.ForeignKey(Coach, null=True, blank=True)

    class Meta:
        verbose_name = _(u'Schedule')
        verbose_name_plural = _(u'Schedules')

    def __unicode__(self):
        return u'%s(%s) %s' % (self.course, self.room, self.begin)

    @property
    def end(self):
        return self.begin + timedelta(minutes=int(60 * self.course.duration))

    def get_calendar_obj(self):
        obj = {
            'id': self.pk,
            'start': self.begin,
            'end': self.end,
            'room': self.room.pk,
            'color': self.room.color,
            'course': self.course.pk,
            'coach': ' '.join([unicode(item) for item in self.course.coach.all()]),
            'room_name': self.room.__unicode__(),
            'title': self.course.__unicode__()
        }
        return obj

    def get_for_user(self, user):
        type = None
        if user is None or self.end < datetime.today():
            type = 'unavailable'
        else:
            cards = Card.objects.filter(client=user, course=self.course, exp_date__gt=datetime.today())
            for item in cards:
                if item.count > 0:
                    type = 'available'
        if type is None:
            type = 'posible'

        obj = {
            'id': self.pk,
            'title': self.course.__unicode__(),
            'room': self.room.__unicode__(),
            'start': self.begin.strftime('%H:%M'),
            'end': self.end.strftime('%H:%M'),
            'coach': ' '.join([str(item) for item in self.course.coach.all()]),
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
                'title': '%s - %s' % (event.course.__unicode__(), event.room.__unicode__()),
                'date': '%s - %s' % (event.begin, event.end)
            }
        except self.DoesNotExist:
            return None

    def get_visitors(self):
        return [(v.client.last_name,
                 v.client.first_name,
                 v.client.rfid_code) for v in self.visit_set.all()]

class Visit(models.Model):
    client = models.ForeignKey(Client)
    schedule = models.ForeignKey(Schedule)
    card = models.ForeignKey(Card, null=True, blank=True)
    when = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)

    class Meta:
        verbose_name = _(u'Visit')
        verbose_name_plural = _(u'Visits')
        unique_together = ('client', 'schedule')

