# -*- coding: utf-8 -*-

from django import forms
from models import Schedule, Course

class ScheduleForm(forms.ModelForm):
    begin = forms.DateTimeField(widget=forms.Select())

    class Meta:
        model = Schedule
        exclude = ('looking', 'places')

    def clean(self):
        from datetime import timedelta
        from django.db.models import Q, F

        room = self.cleaned_data['room']
        begin = self.cleaned_data['begin']
        course = self.cleaned_data['course']
        end = begin + timedelta(hours=course.duration),
        end = end[0]
        result = Schedule.objects.select_related().filter(room=room).filter(begin__day=begin.day)

        for item in result:
            if (begin < item.end < end) or (begin <= item.begin < end):
                raise forms.ValidationError('Incorect begin date')
        return self.cleaned_data