# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.conf import settings
from django import forms
from django.db.models import Q
from django.utils.translation import ugettext as _

from storage import models as storage
from datetime import timedelta, datetime, date

# Create own field to process a list of ids.
class ListField(forms.Field):
    def clean(self, data):
        if data is None:
            return []
        return eval(data)

class StatusForm(forms.ModelForm):
    change_flag = forms.BooleanField(required=False)
    outside = forms.BooleanField(required=False)

    class Meta:
        model = storage.Schedule
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
        model = storage.Schedule
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
            result = storage.Schedule.objects.select_related().filter(room=room).filter(begin__range=(begin.date(), begin.date()+timedelta(days=1)))

            if self.instance.pk:
                result = result.exclude(pk=self.instance.pk)

            for item in result:
                if (begin < item.end < end) or (begin <= item.begin < end):
                    raise forms.ValidationError('Incorect begin date for this room')
        return self.cleaned_data

    def get_errors(self):
        from django.utils.encoding import force_unicode
        return ''.join([force_unicode(v) for k, v in self.errors.items()])

class UserCardForm(forms.ModelForm):
    rfid_code = forms.CharField(max_length=8)

    class Meta:
        model = storage.Card
        exclude = ('reg_date', 'exp_date', 'client')

    def clean_rfid_code(self):
        rfid = self.cleaned_data['rfid_code']
        try:
            user = storage.Client.objects.get(rfid_code=rfid)
            self.cleaned_data['client'] = user
        except storage.Client.DoesNotExist:
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
        if storage.Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
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
        events = storage.Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
        delta = to_date - from_date
        for e in events:
            ne = storage.Schedule(room=e.room, course=e.course)
            ne.begin = e.begin+delta
            ne.save()





class AjaxForm(forms.Form):

    # TODO: check symbols of RFID code

    def param(self, name):
        try:
            return self.cleaned_data[name]
        except KeyError:
            if settings.DEBUG:
                raise forms.ValidationError(_('There is no such key: %s.') % unicode(name))
            else:
                print _('There is no such key: %s.') % unicode(name)

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

    def obj_by_id(self, model, field_name):
        object_name = field_name.split('_')[0]
        object_id = self.cleaned_data[field_name]
        del( self.cleaned_data[field_name] )
        return model.objects.get(id=object_id)

class Login(AjaxForm):
    login = forms.CharField(max_length=30)
    password = forms.CharField(max_length=128)

    def clean_login(self):
        login = self.param('login')
        if len(login) == 0:
            raise forms.ValidationError('Empty login.')
        return login

    def clean_password(self):
        password = self.param('password')
        if len(password) == 0:
            raise forms.ValidationError('Empty password.')
        return password

    def clean(self):
        from django.contrib import auth
        login = self.param('login')
        password = self.param('password')
        user = auth.authenticate(username=login, password=password)
        if user is not None:
            if not user.is_active:
                raise forms.ValidationError('Your account has been disabled!')
            else:
                return self.cleaned_data
        else:
            raise forms.ValidationError('Your username and password were incorrect.')

    def query(self, request):
        from django.contrib import auth
        login = self.param('login')
        password = self.param('password')
        user = auth.authenticate(username=login, password=password)
        if user and user.is_active:
            auth.login(request, user)
            #print request.session.session_key
        return '%s %s' % (user.last_name, user.first_name)

class RegisterVisit(AjaxForm):
    event_id = forms.IntegerField()
    card_id = forms.IntegerField(required=False)
    rfid_code = forms.CharField(max_length=8)

    def clean_client_id(self):
        return self.check_obj_existence(storage.Client, 'client_id')

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def clean(self):
        c = self.cleaned_data
        client = storage.Client.objects.get(rfid_code=c['rfid_code'])
        event = storage.Schedule.objects.get(id=c['event_id'])
        if event.begin <= datetime.now():
            raise forms.ValidationError(_('Avoid the appointment in the past.'))
        if storage.Visit.objects.filter(client=client, schedule=event).count() > 0:
            raise forms.ValidationError(_('The client is already registered on this event.'))
        return self.cleaned_data

    def save(self):
        c = self.cleaned_data
        client = storage.Client.objects.get(rfid_code=c['rfid_code'])
        event = storage.Schedule.objects.get(id=c['event_id'])
        visit = storage.Visit(client=client, schedule=event)
        if c['card_id'] is not None:
            card = storage.Card.objects.get(id=c['card_id'])
            visit.card = card
        visit.save()
        return visit.id

class GetScheduleInfo(AjaxForm):
    id = forms.IntegerField()

    def clean_id(self):
        return self.check_obj_existence(storage.Schedule, 'id')

    def query(self, request=None):
        id = self.cleaned_data['id']
        event = storage.Schedule.objects.get(id=id)
        return event.about()

class UserRFID(forms.Form):
    rfid_code = forms.CharField(max_length=8)

class UserSearch(AjaxForm):
    """ Form searches users using their names and returns users list. """
    name = forms.CharField(max_length=64)
    mode = forms.CharField(max_length=6)

    def query(self, request=None):
        name = self.param('name')
        mode = self.param('mode')
        if mode == 'client':
            model = storage.Client
        else: # renter
            model = storage.Renter
        users = model.objects.filter(Q(first_name=name)|Q(last_name=name))
        return [item.about() for item in users]

class UserInfo(AjaxForm):
    """ Base form for Client and Renter. See below. """
    user_id = forms.IntegerField()
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64)
    email = forms.EmailField(max_length=64)

    def clean_user_id(self):
        return int( self.cleaned_data['user_id'] )

class ClientInfo(UserInfo):
    """ See parent. FIXME """
    rfid_code = forms.CharField(max_length=8)
    course_assigned = ListField(required=False)
    course_cancelled = ListField(required=False)
    course_changed = ListField(required=False)

    def save(self):
        data = self.cleaned_data

        assigned = data['course_assigned']

        user_id = data['user_id']
        for i in ['user_id', 'course_assigned',
                  'course_changed', 'course_cancelled']:
            del(data[i])
        if 0 == user_id:
            user = storage.Client(**data)
        else:
            user = storage.Client.objects.get(id=user_id)
            for key, value in data.items():
                setattr(user, key, value)
        user.save()

        if len(assigned) > 0:
            for id, card_type, bgn_date, exp_date in assigned:
                bgn_date = date(*[int(i) for i in bgn_date.split('-')])
                exp_date = date(*[int(i) for i in exp_date.split('-')])
                course = storage.Course.objects.get(id=id)
                card = storage.Card(
                    course=course, client=user,type=card_type,
                    bgn_date=bgn_date, exp_date=exp_date,
                    count_sold=course.count,
                    price=course.price)
                card.save()

        return user.id

class RenterInfo(UserInfo):
    """ See parent. Form saves and returns the ID of the created
    renter. Also it may just returns the user's info using passed
    ID. """
    phone_mobile = forms.CharField(max_length=16, required=False)
    phone_work = forms.CharField(max_length=16, required=False)
    phone_home = forms.CharField(max_length=16, required=False)

    def save(self):
        data = self.cleaned_data
        user_id = data['user_id']; del(data['user_id'])
        if 0 == user_id:
            user = storage.Renter(**data)
        else:
            user = storage.Renter.objects.get(id=user_id)
            for key, value in data.items():
                setattr(user, key, value)
        user.save()
        return user.id

class UserIdRfid(AjaxForm):
    """ Form returns user's info using passed IDs and mode. """
    user_id = forms.IntegerField(required=False)
    rfid_code = forms.CharField(max_length=8, required=False)
    mode = forms.CharField(max_length=6)

    def query(self, request=None):
        mode = self.param('mode')
        user_id = self.param('user_id')
        if mode == 'client':
            try:
                if user_id is None:
                    user = storage.Client.objects.get(rfid_code=self.param('rfid_code'))
                else:
                    user = storage.Client.objects.get(id=user_id)
            except storage.Client.DoesNotExist:
                return None
        elif mode == 'renter':
            try:
                user = storage.Renter.objects.get(id=user_id)
            except storage.Renter.DoesNotExist:
                return None
        return user.about()

class RegisterRent(AjaxForm):
    """ Form registers the rent and returns its ID. """

    renter_id = forms.IntegerField()
    status = forms.IntegerField()
    title = forms.CharField(max_length=64)
    desc = forms.CharField()
    begin_date = forms.DateField()
    end_date = forms.DateField()
    paid = forms.FloatField()

    def clean_renter_id(self):
        return self.check_obj_existence(storage.Renter, 'renter_id')

    # FIXME: Add the status range check

    def clean(self):
        data = self.cleaned_data
        begin = data['begin_date']
        end = data['end_date']
        if begin < date.today():
            raise forms.ValidationError(_('Avoid a rent assignment in the past.'))
        if end < begin:
            raise forms.ValidationError(_('Exchange the dates.'))
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        data.update( {'renter': self.obj_by_id(storage.Renter, 'renter_id')} )
        rent = storage.Rent(**data)
        rent.save()
        return rent.id

class DateRange(AjaxForm):
    """ Form acquires a date range and return the list of events inside
    this range. """
    monday = forms.DateField()
    filter = ListField(required=False)

    def query(self, request=None):
        filter = self.cleaned_data['filter']
        monday = self.cleaned_data['monday']
        limit = monday + timedelta(days=7)
        schedules = storage.Schedule.objects.filter(begin__range=(monday, limit))
        if len(filter) > 0:
            schedules = schedules.filter(room__in=c['filter'])
        events = [item.about() for item in schedules]
        return events

class CalendarEventAdd(AjaxForm):
    """ Form creates new event using a passing datas. """
    event_id = forms.IntegerField()
    room_id = forms.IntegerField()
    begin = forms.DateTimeField()
    ev_type = forms.IntegerField()
    duration = forms.FloatField(required=False)

    def clean_course_id(self):
        return self.check_obj_existence(storage.Course, 'course_id')

    def clean_room_id(self):
        return self.check_obj_existence(storage.Room, 'room_id')

    def clean_begin(self):
        return self.check_future('begin')

    def clean(self):
        data = self.cleaned_data

        room = storage.Room.objects.get(id=data['room_id'])
        begin = data['begin']
        if data['ev_type'] == 0:
            obj = storage.Course.objects.get(id=data['event_id'])
            end = begin + timedelta(minutes=(60 * obj.duration))
        else:
            end = begin + timedelta(minutes=(60 * data['duration']))

        today = date.today()
        if storage.Schedule.objects.filter(
            room=room,
            begin__year=today.year,
            begin__month=today.month,
            begin__day=today.day
            ).filter(begin__lte=end).filter(end__gt=begin).count() != 0:
            raise forms.ValidationError(_('There is an event intersection.'))
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        ev_type = data['ev_type']
        room = storage.Room.objects.get(id=data['room_id'])
        begin = data['begin']
        if ev_type == 0:
            obj = storage.Course.objects.get(id=data['event_id'])
            end = begin + timedelta(minutes=(60 * obj.duration))
            event = storage.Schedule(
                course= obj, room=room, status=0,
                begin=begin, end=end, duration=obj.duration)
        else:
            end = begin + timedelta(minutes=(60 * data['duration']))
            event = storage.Schedule(
                rent=storage.Rent.objects.get(id=data['event_id']),
                room=room, status=0,
                begin=begin, end=end, duration=data['duration'])
        event.save()
        return event.id

class CalendarEventDel(AjaxForm):
    """ Form acquires an event ID and deletes appropriate event. """
    id = forms.IntegerField()

    def clean_id(self):
        return self.check_obj_existence(storage.Schedule, 'id')

    def remove(self):
        c = self.cleaned_data
        storage.Schedule.objects.get(id=c['id']).delete()

class ExchangeRoom(AjaxForm):
    """ Form acquires the IDs of two events and tries to exchange their
    rooms."""
    id_a = forms.IntegerField()
    id_b = forms.IntegerField()

    def event_intersection(self, event_a, event_b):
        """ Метод для определения пересечения событий по времени. """
        a1 = event_a.begin
        a2 = a1 + timedelta(minutes=int(60 * event_a.duration))
        b1 = event_b.begin
        b2 = b1 + timedelta(minutes=int(60 * event_b.duration))

        if a1 <= b1 < a2 <= b2:
            return True
        if b1 <= a1 < b2 <= a2:
            return True
        if a1 <= b1 < b2 <= a2:
            return True
        if b1 <= a1 < a2 <= b2:
            return True
        return False

    def clean(self):
        data = self.cleaned_data
        try:
            event_a = storage.Schedule.objects.get(id=int(data['id_a']))
            event_b = storage.Schedule.objects.get(id=int(data['id_b']))
        except:
            raise forms.ValidationError(_('Check event IDs.'))

        if event_a == event_b:
            raise forms.ValidationError(_('Unable to exchange the same event.'))

        if not self.event_intersection(event_a, event_b):
            raise forms.ValidationError(_('There is no event intersection.'))

        # события совпадают по времени начала и длительности
        if event_a.begin == event_b.begin and \
                event_a.duration == event_a.duration:
            return self.cleaned_data

        return self.cleaned_data # СДЕЛАТЬ ПРОВЕРКИ ПОЛНОСТЬЮ
        raise forms.ValidationError(_('Not implemented yet.'))


#         if storage.Schedule.objects.filter(
#             room=room,
#             begin__year=today.year,
#             begin__month=today.month,
#             begin__day=today.day
#             ).filter(begin__lte=end).filter(end__gt=begin).count() != 0:
#             raise forms.ValidationError(_('There is an event intersection.'))



    def save(self):
        data = self.cleaned_data
        print data

        event_a = storage.Schedule.objects.get(id=int(data['id_a']))
        event_b = storage.Schedule.objects.get(id=int(data['id_b']))

        print event_a, event_a.room
        print event_b, event_b.room

        room_tmp = event_a.room
        event_a.room = event_b.room
        event_b.room = room_tmp

        print event_a, event_a.room
        print event_b, event_b.room

        event_a.save()
        event_b.save()

class CopyWeek(AjaxForm):
    """ Form acquires two dates and makes a copy from first one to
    second. """
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
        if storage.Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
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
        events = storage.Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
        delta = to_date - from_date
        for e in events:
            ne = storage.Schedule(room=e.room, course=e.course,
                                  rent=e.rent, status=0,
                                  duration=e.duration)
            ne.begin = e.begin+delta
            ne.end = ne.begin + timedelta(minutes=(60 * e.duration))
            ne.save()

class GetVisitors(AjaxForm):
    """ Form acquires an event ID and returns the list of visitors. """
    event_id = forms.IntegerField()

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def query(self, request=None):
        event_id = self.cleaned_data['event_id']
        event = storage.Schedule.objects.get(id=event_id)
        return event.get_visitors()
