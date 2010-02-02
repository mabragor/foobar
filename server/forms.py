# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class Login(forms.Form):
    login = forms.CharField(label=_('Login'), max_length=30,
                            widget=forms.TextInput(attrs={'class': 'field'}))
    passwd = forms.CharField(label=_('Password'), max_length=30,
                             widget=forms.PasswordInput(attrs={'class': 'field'}))
