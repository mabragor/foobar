# -*- coding: utf-8 -*-

from django import forms
from storage.models import Schedule, Card, Client
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta, datetime, date

class StatusForm(forms.ModelForm):
    change_flag = forms.BooleanField(required=False)
    outside = forms.BooleanField(required=False)

    class Meta:
        model = Schedule
        exclude = ('room', 'course', 'begin', 'looking', 'places')

    def clean(self):
        data = self.cleaned_data
        if not data.get('change_flag', None):
            if 'outside' in data:
                del data['outside']
            if 'change' in data:
                del data['change']
        elif not (data.get('change', False) or data.get('outside', False)):
            raise forms.ValidationError('Set coach to change.')
        elif data['outside']:
            if 'change' in data:
                del data['change']
        return data

    def get_errors(self):
        #FIXME: get_errors method is used in multiple forms(DRY)
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule
        exclude = ('looking', 'places', 'change', 'status')

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

class UserCardForm(forms.ModelForm):
    rfid_code = forms.CharField(max_length=8)

    class Meta:
        model = Card
        exclude = ('reg_date', 'exp_date', 'client')

    def clean_rfid_code(self):
        rfid = self.cleaned_data['rfid_code']
        try:
            user = Client.objects.get(rfid_code=rfid)
            self.cleaned_data['client'] = user
        except Client.DoesNotExist:
            raise form.ValidationError('Undefined rfid code.')
        return user

    def save(self, commit=True):
        obj = super(UserCardForm, self).save(commit=False)
        obj.client = self.cleaned_data['client']
        obj.exp_date = datetime.now() + timedelta(days=30)
        obj.save(commit)
        return obj

    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

class CopyForm(forms.Form):
    from_date = forms.DateField()
    to_date = forms.DateField()

    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

    def validate_date(self, date):
        if not date.weekday() ==  0:
            raise forms.ValidationError('Date must be a Monday.')
        return date

    def clean_from_date(self):
        return self.validate_date(self.cleaned_data['from_date'])

    def clean_to_date(self):
        to_date = self.validate_date(self.cleaned_data['to_date'])
        print to_date
        if to_date < date.today():
            raise forms.ValidationError('Can not paste events into the past.')
        if Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
            raise forms.ValidationError('Week must be empty to paste events.')
        return to_date

    def clean(self):
        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        if from_date and to_date and from_date == to_date:
            raise forms.ValidationError('Copy to the same week.')
        return self.cleaned_data

    def save(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        events = Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
        for e in events:
            ne = Schedule(room=e.room, course=e.course)
            ne.begin = e.begin+timedelta(days=7)
            ne.save()

