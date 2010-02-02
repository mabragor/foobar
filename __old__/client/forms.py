# -*- coding: utf-8 -*-

from django import forms
from storage.models import Schedule, Course

class ActiveCourses(forms.Form):
    rfid_code = forms.CharField(max_length=8)
