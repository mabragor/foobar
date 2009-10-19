# -*- coding: utf-8 -*-

from django import forms
from storage.models import Schedule, Course
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime

class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule
        exclude = ('looking', 'places')

    def clean_begin(self):
        begin = self.cleaned_data['begin']
        if begin < datetime.now():
            raise forms.ValidationError('Can not create event in the past.')
        return begin

    def clean(self):
        room = self.cleaned_data['room']
        begin = self.cleaned_data.get('begin')
        course = self.cleaned_data['course']
        if room and begin and course:
            end = begin + timedelta(hours=course.duration)
            result = Schedule.objects.select_related().filter(room=room).filter(begin__day=begin.day)

            for item in result:
                if (begin < item.end < end) or (begin <= item.begin < end):
                    raise forms.ValidationError('Incorect begin date for this room')
        return self.cleaned_data

    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

class UserRFID(forms.Form):
    rfid_code = forms.CharField(max_length=8)
