# -*- coding: utf-8 -*-
from django import forms
from models import Schedule

class ScheduleForm(forms.ModelForm):
    begin = forms.DateTimeField(widget=forms.Select())

    class Meta:
        model = Schedule
        exclude = ('week_day', 'looking', 'places')