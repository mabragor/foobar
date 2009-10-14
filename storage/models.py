# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta

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
    pass

class Client(AbstractUser):
    pass

class Room(models.Model):
    title = models.CharField(verbose_name=_(u'Title'), max_length=64)
    color = models.CharField(verbose_name=_(u'Color'), max_length=6)

    def get_calendar_obj(self):
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
            'children': [item.get_tree_node() for item in self.course_set.all()]
        }
        return obj

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

class Card(models.Model):
    course = models.ForeignKey(Course)
    client = models.ForeignKey(Client)
    reg_date = models.DateTimeField(verbose_name=_(u'Registered'), auto_now_add=True)
    exp_date = models.DateTimeField(verbose_name=_(u'Expired'))
    count = models.IntegerField(verbose_name=_(u'Count'))

    class Meta:
        verbose_name = _(u'Card')
        verbose_name_plural = _(u'Card')

    def __unicode__(self):
        return self.course.title

class Schedule(models.Model):
    room = models.ForeignKey(Room)
    course = models.ForeignKey(Course)
    begin = models.DateTimeField(verbose_name=_(u'Begins'))
    looking = models.BooleanField(verbose_name=_(u'Is looking for members?'), default=True)
    places = models.BooleanField(verbose_name=_(u'Are there free places?'), default=True)

    @property
    def end(self):
        return self.begin + timedelta(hours=self.course.duration)

    def get_calendar_obj(self):
        obj = {
            'id': self.pk,
            'start': self.begin,
            'end': self.begin + timedelta(hours=self.course.duration),
            'room': self.room.pk,
            'color': self.room.color,
            'course': self.course.pk,
            'room_name': self.room.__unicode__(),
            'title': self.course.__unicode__()
        }
        return obj

    class Meta:
        verbose_name = _(u'Schedule')
        verbose_name_plural = _(u'Schedules')

class Action(models.Model):
    ACTION_STATUSES = (
        ('1', _('Done')),
        ('2', _('Cancel')),
        )
    schedule = models.ForeignKey(Schedule)
    card = models.ForeignKey(Card)
    change = models.ForeignKey(Coach)
    when = models.DateTimeField(verbose_name=_(u'Registered'))
    status = models.CharField(verbose_name=_(u'Status'), max_length=1, choices=ACTION_STATUSES)

    class Meta:
        verbose_name = _(u'Action')
        verbose_name_plural = _(u'Actions')

