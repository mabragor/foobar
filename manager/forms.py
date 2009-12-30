# -*- coding: utf-8 -*-

from django import forms
from storage.models import Schedule, Card, Client, Course, Room
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
            result = Schedule.objects.select_related().filter(room=room).filter(begin__range=(begin.date(), begin.date()+timedelta(days=1)))

            if self.instance.pk:
                result = result.exclude(pk=self.instance.pk)

            for item in result:
                #print item.course.__unicode__()
                if (begin < item.end < end) or (begin <= item.begin < end):
                    raise forms.ValidationError('Incorect begin date for this room')
        return self.cleaned_data

    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

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
        delta = to_date - from_date
        for e in events:
            ne = Schedule(room=e.room, course=e.course)
            ne.begin = e.begin+delta
            ne.save()





class AjaxForm(forms.Form):
    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

    def check_obj_existence(self, model, field_name):
        value = self.cleaned_data[field_name]
        try:
            model.objects.get(id=value)
        except model.DoesNotExist:
            raise forms.ValidationError(_('Wrong ID of %s.') % unicode(model))
        return value

    def check_future(self,field_name):
        value = self.cleaned_data[field_name]
        if type(value) is date:
            if value <= date.today():
                raise forms.ValidationError(_('Date has to be in the future.'))
        elif type(value) is datetime:
            if value <= datetime.now():
                raise forms.ValidationError(_('Date has to be in the future.'))
        else:
            raise forms.ValidationError(_('Unsupported type.'))
        return value

class OnlyID(AjaxForm):
    id = forms.IntegerField()

    def query(self):
        id = self.cleaned_data['id']
        event = Schedule.objects.get(id=id)
        info = event.get_calendar_obj()
        return info

class UserRFID(forms.Form):
    rfid_code = forms.CharField(max_length=8)

class UserName(forms.Form):
    name = forms.CharField(max_length=64)

# Create own field to process a list of ids.
class ListField(forms.Field):
    def clean(self, data):
        if data is None:
            return []
        return eval(data)

class UserInfo(forms.Form):
    user_id = forms.IntegerField()
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    email = forms.EmailField(max_length=64)
    rfid_code = forms.CharField(max_length=8)
    course_assigned = ListField(required=False)
    course_cancelled = ListField(required=False)
    course_changed = ListField(required=False)

class DateRange(AjaxForm):
    monday = forms.DateField()
    filter = ListField(required=False)

    def query(self):
        filter = self.cleaned_data['filter']
        monday = self.cleaned_data['monday']
        limit = monday + timedelta(days=7)
        schedules = Schedule.objects.filter(begin__range=(monday, limit))
        if len(filter) > 0:
            schedules = schedules.filter(room__in=c['filter'])
        events = [item.get_calendar_obj() for item in schedules]
        return events

class CalendarEventAdd(AjaxForm):
    course_id = forms.IntegerField()
    room_id = forms.IntegerField()
    begin = forms.DateTimeField()
    ev_type = forms.IntegerField()

    def clean_course_id(self):
        return self.check_obj_existence(Course, 'course_id')

    def clean_room_id(self):
        return self.check_obj_existence(Room, 'room_id')

    def clean_begin(self):
        return self.check_future('begin')

    def save(self):
        c = self.cleaned_data
        course = Course.objects.get(id=c['course_id'])
        room = Room.objects.get(id=c['room_id'])
        begin = c['begin']
        ev_type = c['ev_type']
        Schedule(course=course, room=room, begin=begin, status=0).save()

class CopyWeek(AjaxForm):
    from_date = forms.DateField()
    to_date = forms.DateField()

    def validate_date(self, date):
        if not date.weekday() ==  0:
            raise forms.ValidationError(_('Date must be Monday.'))
        return date

    def clean_from_date(self):
        return self.validate_date(self.cleaned_data['from_date'])

    def clean_to_date(self):
        to_date = self.validate_date(self.cleaned_data['to_date'])
        if to_date < date.today():
            raise forms.ValidationError(_('It is impossible to copy events to the past.'))
        if Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
            raise forms.ValidationError('Week must be empty to paste events.')
        return to_date

    def clean(self):
        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        if from_date and to_date and from_date == to_date:
            raise forms.ValidationError(_('It is impossible to copy the week into itself.'))
        return self.cleaned_data

    def save(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        events = Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
        delta = to_date - from_date
        for e in events:
            ne = Schedule(room=e.room, course=e.course)
            ne.begin = e.begin+delta
            ne.save()
