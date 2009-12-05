# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime
from django.conf import settings

class AbstractUser(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64, blank=True, null=True)
    rfid_code = models.CharField(max_length=8)
    reg_date = models.DateTimeField(verbose_name=_('Registered'), auto_now_add=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode('%s %s' % (self.first_name, self.last_name))

class Coach(AbstractUser):

    def get_store_obj(self):
        obj = {
            'id': self.pk,
            'name': self.__unicode__()
        }
        return obj

class Client(AbstractUser):

    def get_course_list(self):
        return [card.get_info() for card in self.card_set.all()]

class Room(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    color = models.CharField(verbose_name=_(u'Color'), max_length=6)

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

    class Meta:
        verbose_name = _(u'Room')
        verbose_name_plural = _(u'Rooms')

    def __unicode__(self):
        return self.title

class Group(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)

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

    class Meta:
        verbose_name = _(u'Style')
        verbose_name_plural = _(u'Styles')

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
    course = models.ForeignKey(Course)
    client = models.ForeignKey(Client)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    exp_date = models.DateTimeField(verbose_name=_(u'Expired'))
    count = models.IntegerField(verbose_name=_(u'Count'))

    class Meta:
        verbose_name = _(u'Card')
        verbose_name_plural = _(u'Card')
        ordering = ['-reg_date']

    def __unicode__(self):
        return self.course.title

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

    def get_info(self):
        return {
            'id': self.pk,
            'title': self.course.title,
            'course_id': self.course.pk,
            'reg_date': self.reg_date,
            'exp_date': self.exp_date,
            'count': self.count,
            'deleteable': False,#self.deleteable(),
            'is_old': self.is_old()
        }

class Schedule(models.Model):
    ACTION_STATUSES = (
        ('1', _('Done')),
        ('2', _('Cancel')),
    )
    room = models.ForeignKey(Room)
    course = models.ForeignKey(Course)
    begin = models.DateTimeField(verbose_name=_(u'Begins'))
    looking = models.BooleanField(verbose_name=_(u'Is looking for members?'), default=True)
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
        return self.begin + timedelta(hours=self.course.duration)

    def get_calendar_obj(self):
        obj = {
            'id': self.pk,
            'start': self.begin,
            'end': self.end,
            'room': self.room.pk,
            'color': self.room.color,
            'course': self.course.pk,
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

class Action(models.Model):
    schedule = models.ForeignKey(Schedule)
    card = models.ForeignKey(Card)
    when = models.DateTimeField(verbose_name=_(u'Registered'))

    class Meta:
        verbose_name = _(u'Action')
        verbose_name_plural = _(u'Actions')

