# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.conf import settings
from django import forms
from django.db.models import Q, F
from django.utils.translation import ugettext as _

from storage import models as storage
from datetime import timedelta, datetime, date

class AjaxForm(forms.Form):

    def dump(self, value):
        import pprint
        pprint.pprint(value)

    def param(self, name):
        """ This method gets the value from cleaned_data by its keyword. """
        try:
            return self.cleaned_data[name]
        except KeyError:
            message = _(u'There is no such key: %s.') % unicode(name)
            if settings.DEBUG:
                raise forms.ValidationError(message)
            else:
                print message

    def check_obj_existence(self, model, field_name):
        """ This method check object existence and saving the object into the
        class. """
        value = self.cleaned_data[field_name]
        try:
            item = model.objects.get(id=value)
        except model.DoesNotExist:
            raise forms.ValidationError(_(u'Wrong ID of %s.') % unicode(model))
        setattr(self, 'object_%s' % field_name, item)
        return value

    def get_object(self, field_name):
        """ This method returns the previously saved object. """
        object = getattr(self, 'object_%s' % field_name, None)
        if not object:
            raise forms.ValidationError(_(u'No such object.'))
        else:
            return object

    def obj_by_id(self, model, field_name):
        """ This method returns object by its ID field name. """
        object_name = field_name.split('_')[0]
        object_id = self.cleaned_data[field_name]
        del( self.cleaned_data[field_name] )
        return model.objects.get(id=object_id)

    def check_future(self,field_name):
        value = self.cleaned_data[field_name]
        if type(value) is date:
            if value <= date.today():
                raise forms.ValidationError(_(u'Date has to be in the future.'))
        elif type(value) is datetime:
            if value <= datetime.now():
                raise forms.ValidationError(_(u'Date has to be in the future.'))
        else:
            raise forms.ValidationError(_(u'Unsupported type.'))
        return value

    def rfid_validation(self, value):
        hex_values = [str(i) for i in xrange(10)] + [a for a in 'ABCDEF']
        for i in value:
            if i.upper() not in hex_values:
                raise forms.ValidationError(_(u'RFID has to consist of HEX symbols.'))

    def rfid_client(self, value):
        try:
            return storage.Client.objects.get(rfid_code=value)
        except storage.Client.DoesNotExist:
            raise forms.ValidationError(_(u'No client for a given RFID.'))

    def get_errors(self):
        from django.utils.encoding import force_unicode
        response = []
        for k,v in self.errors.items():
            response.append( force_unicode(v.as_text()) )
        return '\n'.join(response)

class Login(AjaxForm):
    login = forms.CharField(max_length=30)
    password = forms.CharField(max_length=128)

    def clean_login(self):
        login = self.param('login')
        if len(login) == 0:
            raise forms.ValidationError(_(u'Empty login.'))
        return login

    def clean_password(self):
        password = self.param('password')
        if len(password) == 0:
            raise forms.ValidationError(_(u'Empty password.'))
        return password

    def clean(self):
        from django.contrib import auth
        login = self.param('login')
        password = self.param('password')
        user = auth.authenticate(username=login, password=password)
        if user is not None:
            if not user.is_active:
                raise forms.ValidationError(_(u'Your account has been disabled!'))
            else:
                return self.cleaned_data
        else:
            raise forms.ValidationError(_(u'Your username and password were incorrect.'))

    def query(self, request):
        from django.contrib import auth
        login = self.param('login')
        password = self.param('password')
        user = auth.authenticate(username=login, password=password)
        if user and user.is_active:
            auth.login(request, user)
        return '%s %s' % (user.last_name, user.first_name)

class RegisterVisit(AjaxForm):
    event_id = forms.IntegerField()
    client_id = forms.IntegerField()

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def clean_client_id(self):
        return self.check_obj_existence(storage.Client, 'client_id')

    def clean(self):
        self.client = self.get_object('client_id')
        self.event = self.get_object('event_id')

        if self.event.begin_datetime <= datetime.now():
            raise forms.ValidationError(_(u'Avoid the appointment in the past.'))
        if storage.Visit.objects.filter(client=self.client, schedule=self.event).count() > 0:
            raise forms.ValidationError(_(u'The client is already registered on this event.'))

        # client and event attributes are defined in parent class
        available_cards = storage.Card.objects.filter(
            client=self.client,
            cancel_datetime=None,
            count_used__lt=F('count_available'),
            price_category__full_price__gte=self.event.team.price_category.full_price
            #end_date__lte=date.today() // new card has null here
            )
        if len(available_cards) > 0:
            print 'Available card list:', available_cards
            # sort by priority
            FIELD_PK = 0
            FIELD_PRIORITY = 1
            sorting = []
            for card in available_cards:
                obj = card.card_ordinary or card.card_club or card.card_promo
                sorting.append( (card.pk, obj.priority, card) )
            sorted(sorting, key=lambda x: x[FIELD_PRIORITY])

            # find the appropriate card
            for i in sorting:
                card = available_cards.get(pk=i[FIELD_PK]) # get by pk
                if card.may_register():
                    self.chosen_card = card
                    return self.cleaned_data

        raise forms.ValidationError(_(u'The client has no card of needed category.'))

    def save(self):

        visit = storage.Visit(client=self.client, schedule=self.event)
        visit.card = self.chosen_card # see clean() method
        visit.save()
        return visit.id

class PaymentAdd (AjaxForm):
    """ Form registers client credit payments. """
    card_id = forms.IntegerField()
    amount = forms.FloatField()

    def clean_card_id(self):
        """ Validation of card_id field. """
        return self.check_obj_existence(storage.Card, 'card_id')

    def clean_amount(self):
        """ Validation of amount field. """
        amount = float(self.param('amount'))
        card = self.get_object('card_id')
        if card.paid + amount > card.price:
            needed_payment = card.price - card.paid
            raise forms.ValidationError(_(u'Too much money. Payment is %f.') % needed_payment)
        return amount

    def save(self):
        """ Saving information. """
        card = self.get_object('card_id')
        card.paid += self.param('amount')
        card.save()
        return card.id

class GetScheduleInfo(AjaxForm):
    id = forms.IntegerField()

    def clean_id(self):
        return self.check_obj_existence(storage.Schedule, 'id')

    def query(self, request=None):
        event = self.get_object('id')
        return event.about()

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

class UserIdRfid(AjaxForm):
    """ Form returns user's info using passed IDs and mode. """
    user_id = forms.IntegerField(required=False)
    rfid_code = forms.CharField(max_length=8, required=False)
    mode = forms.CharField(max_length=6)

    def query(self, request=None):
        mode = self.param('mode')
        user_id = self.param('user_id')
        rfid = self.param('rfid_code')

        if mode == 'client':
            try:
                if user_id is None:
                    user = storage.Client.objects.get(rfid_code=rfid)
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
    phone = forms.CharField(max_length=16)
    discount = forms.IntegerField()
    birth_date = forms.DateField()
    rfid_code = forms.CharField(max_length=8, required=False)

    def clean_phone(self):
        value = self.param('phone')
        if len(value) == 0:
            raise forms.ValidationError(_(u'Field "Phone" is empty.'))
        return value

    def clean_rfid_code(self):
        value = self.cleaned_data.get('rfid_code', None)
        # if this code is used while we trying to register new user
        if value and self.param('user_id') == '0' and \
               storage.Client.objects.filter(rfid_code=value).count() > 0:
            raise forms.ValidationError(_(u'This RFID label is used already.'))
        return value

    def save(self):
        data = self.cleaned_data

        user_id = data['user_id']; del( data['user_id'] )
        data['discount'] = storage.Discount.objects.get(id=data['discount'])

        if 0 == user_id:
            user = storage.Client(**data)
        else:
            user = storage.Client.objects.get(id=user_id)
            for key, value in data.items():
                setattr(user, key, value)
        user.save()

        OUTFLOW = '1'
        RFIDCARDS = '0'

        flow = storage.Flow(user=self.request.user, # see deco
                            action=OUTFLOW,
                            type=RFIDCARDS,
                            count=1,
                            price=30.00, # FIXME
                            total=30.00 # FIXME
                            )
        #flow.save()
        return user.id

class ClientCard(AjaxForm):
    client = forms.IntegerField()
    id = forms.IntegerField(required=False)
    card_type = forms.CharField(max_length=64)
    card_meta = forms.CharField(max_length=64, required=False)
    discount = forms.IntegerField()
    price_category = forms.IntegerField(required=False)
    price = forms.FloatField()
    paid = forms.FloatField()
    count_sold = forms.IntegerField()
    count_used = forms.IntegerField()
    count_available = forms.IntegerField()
    begin_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    reg_datetime = forms.DateTimeField()
    cancel_datetime = forms.DateTimeField(required=False)

    def clean_client(self):
        return self.check_obj_existence(storage.Client, 'client')

    def clean_discount(self):
        return self.check_obj_existence(storage.Discount, 'discount')

    def clean_price_category(self):
        if not self.param('price_category'):
            return None
        return self.check_obj_existence(storage.PriceCategoryTeam, 'price_category')

    def save(self):
        data = self.cleaned_data
        card_id = data['id']
        if card_id == 0:
            del(data['id'])

        if data['card_type'] == 'promo':
            data['card_promo'] = storage.CardPromo.objects.get(slug=data['card_meta'])
        elif data['card_type'] == 'club':
            data['card_club'] = storage.CardClub.objects.get(slug=data['card_meta'])
        else: # flyer, test, once, abonement
            data['card_ordinary'] = storage.CardOrdinary.objects.get(slug=data['card_type'])
            card_type = data['card_type']

            del(data['card_type'])
            del(data['card_meta'])

            data['discount'] = self.get_object('discount')
            data['price_category'] = self.get_object('price_category')

        if 0 == card_id: # create new card
            data['client'] = self.get_object('client')
            card = storage.Card(**data)
        else: # edit the existed one
            card = storage.Card.objects.get(id=card_id)
            # ...
        card.save()

class RenterInfo(UserInfo):
    """ See parent. Form saves and returns the ID of the created
    renter. Also it may just update the renter's info using passed
    ID. """
    phone_mobile = forms.CharField(max_length=16, required=False)
    phone_work = forms.CharField(max_length=16, required=False)
    phone_home = forms.CharField(max_length=16, required=False)

    def clean(self):
        if len(self.param('phone_mobile')) == 0 and \
                len(self.param('phone_work')) == 0 and \
                len(self.param('phone_home')) == 0:
            raise forms.ValidationError(_(u'At least one phone number must be filled.'))
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        renter_id = data['user_id'];
        if 0 == renter_id:
            renter = storage.Renter(**data)
        else:
            renter = storage.Renter.objects.get(id=renter_id)
            for key, value in data.items():
                setattr(renter, key, value)
        renter.save()
        return renter.id

class RenterCard(AjaxForm):
    """ Form registers/updates the rent and returns its ID. """

    renter = forms.IntegerField()
    id = forms.IntegerField() # rent_id
    status = forms.IntegerField()
    title = forms.CharField(max_length=64)
    desc = forms.CharField()
    begin_date = forms.DateField()
    end_date = forms.DateField()
    paid = forms.FloatField()

    def clean_renter(self):
        return self.check_obj_existence(storage.Renter, 'renter')

    # FIXME: Add the status range check

    def clean(self):
        rent_id = self.cleaned_data['id']
        begin = self.cleaned_data['begin_date']
        end = self.cleaned_data['end_date']

        # don't allow to create rent for dates in the past
        if rent_id == 0 and begin < date.today():
            raise forms.ValidationError(_(u'Avoid a rent assignment in the past.'))

        # check dates
        if end < begin:
            raise forms.ValidationError(_(u'Exchange the dates.'))
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        renter = self.get_object('renter')

        rent_id = data['id']
        if rent_id == 0:
            rent = storage.Rent(renter=renter,
                                status=data['status'],
                                title=data['title'],
                                desc=data['desc'],
                                begin_date=data['begin_date'],
                                end_date=data['end_date'],
                                paid=data['paid'])
        else:
            rent = storage.Rent.objects.get(id=rent_id)
            rent.status = data['status']
            rent.title=data['title']
            rent.desc=data['desc']
            rent.begin_date=data['begin_date']
            rent.end_date=data['end_date']
            rent.paid=data['paid']
        rent.save()
        return rent.id

class RegisterChange(AjaxForm):
    """ Form registers the coach's change for the event. """

    event_id = forms.IntegerField()
    coach_id_list = forms.CharField(max_length=256)

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def clean_coach_id_list(self):
        coaches_id = self.cleaned_data['coach_id_list'].split(',')
        coaches_list = []
        for coach_id in coaches_id:
            coaches_list.append(storage.Coach.objects.get(id=int(coach_id)))
        return coaches_list

    def save(self):
        event = self.get_object('event_id')
        coaches_list = self.cleaned_data['coach_id_list']
        event.coaches.clear()
        for i in coaches_list:
            event.coaches.add(i)
        event.save()
        return event.id

class RegisterFix(AjaxForm):
    """ Form registers the event's fix status. """

    event_id = forms.IntegerField()
    fix_id = forms.IntegerField()

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def save(self):
        event = self.get_object('event_id')
        fix = self.param('fix_id')
        event.status = fix
        event.save()
        return event.id

# Create own field to process a list of ids.
class ListField(forms.Field):
    def clean(self, data):
        if data is None:
            return []
        return eval(data)

class DateRange(AjaxForm):
    """ Form acquires a date range and return the list of events inside
    this range. See manager:event_storage:loadData(). """
    monday = forms.DateField()
    filter = ListField(required=False)

    def query(self, request=None):
        filter = self.param('filter')
        monday = self.param('monday')
        limit = monday + timedelta(days=7)
        schedules = storage.Schedule.objects.filter(begin_datetime__range=(monday, limit))

        if len(filter) > 0:
            schedules = schedules.filter(room__in=filter)
        events = [item.about() for item in schedules]
        return events

class CalendarEventAdd(AjaxForm):
    """ Form creates new event using a passing datas. """
    event_id = forms.IntegerField()
    room_id = forms.IntegerField()
    begin = forms.DateTimeField()
    ev_type = forms.IntegerField()
    duration = forms.FloatField(required=False)

    def clean_team_id(self):
        return self.check_obj_existence(storage.Team, 'team_id')

    def clean_room_id(self):
        return self.check_obj_existence(storage.Room, 'room_id')

    def clean_begin(self):
        return self.check_future('begin')

    def clean(self):
        data = self.cleaned_data

        room = storage.Room.objects.get(id=data['room_id'])
        begin = data['begin']
        if data['ev_type'] == 0:
            obj = storage.Team.objects.get(id=data['event_id'])
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
            raise forms.ValidationError(_(u'There is an event intersection.'))
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        ev_type = data['ev_type']
        room = storage.Room.objects.get(id=data['room_id'])
        begin = data['begin']
        if ev_type == 0:
            obj = storage.Team.objects.get(id=data['event_id'])
            end = begin + timedelta(minutes=(60 * obj.duration))
            event = storage.Schedule(
                team= obj, room=room, status=0, fixed=0,
                begin=begin, end=end, duration=obj.duration)
        else:
            end = begin + timedelta(minutes=(60 * data['duration']))
            obj = storage.Rent.objects.get(id=data['event_id'])
            event = storage.Schedule(
                rent=obj, room=room, status=0, fixed=0,
                begin=begin, end=end, duration=data['duration'])
        event.save()
        return event.id

class CalendarEventDel(AjaxForm):
    """ Form acquires an event ID and deletes appropriate event. """
    id = forms.IntegerField()

    def clean_id(self):
        return self.check_obj_existence(storage.Schedule, 'id')

    def clean(self):
        id = self.cleaned_data['id']
        event = storage.Schedule.objects.get(id=id)
        if event.begin_datetime < datetime.now():
            raise forms.ValidationError(_(u'Unable to delete this event.'))
        return self.cleaned_data

    def remove(self):
        c = self.cleaned_data
        event = storage.Schedule.objects.get(id=c['id'])
        event.delete()

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
            raise forms.ValidationError(_(u'Check event IDs.'))

        if event_a == event_b:
            raise forms.ValidationError(_(u'Unable to exchange the same event.'))

        if not self.event_intersection(event_a, event_b):
            raise forms.ValidationError(_(u'There is no event intersection.'))

        # события совпадают по времени начала и длительности
        if event_a.begin == event_b.begin and \
                event_a.duration == event_a.duration:
            return self.cleaned_data

        return self.cleaned_data # СДЕЛАТЬ ПРОВЕРКИ ПОЛНОСТЬЮ
        raise forms.ValidationError(_(u'Not implemented yet.'))


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
            raise forms.ValidationError(_(u'Date must be Monday.'))
        return date

    def clean_from_date(self):
        return self.validate_date(self.cleaned_data['from_date'])

    def clean_to_date(self):
        to_date = self.validate_date(self.cleaned_data['to_date'])
        if to_date < date.today():
            raise forms.ValidationError(_(u'It is impossible to copy events to the past.'))
        if storage.Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
            raise forms.ValidationError(u'Week must be empty to paste events.')
        return to_date

    def clean(self):
        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        if from_date and to_date and from_date == to_date:
            raise forms.ValidationError(_(u'It is impossible to copy the week into itself.'))
        return self.cleaned_data

    def save(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        events = storage.Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
        delta = to_date - from_date
        for e in events:
            ne = storage.Schedule(room=e.room, team=e.team,
                                  rent=e.rent, status=0, fixed=0,
                                  duration=e.duration)
            ne.begin = e.begin+delta
            ne.end = ne.begin + timedelta(minutes=(60 * e.duration))
            ne.save()

class FillWeek(AjaxForm):
    """ Form acquires a date and makes a copy from calendar to
schedule. """
    to_date = forms.DateField()

    def validate_date(self, date):
        if not date.weekday() ==  0:
            raise forms.ValidationError(_(u'Date must be Monday.'))
        return date

    def clean_to_date(self):
        to_date = self.validate_date(self.cleaned_data['to_date'])
#         if to_date < date.today():
#             raise forms.ValidationError(_(u'It is impossible to copy events to the past.'))
#         if storage.Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
#             raise forms.ValidationError(u'Week must be empty to paste events.')
        return to_date

    def save(self):
        week_start = self.cleaned_data.get('to_date')
        calendar = storage.Calendar.objects.all()

        count_copied = count_passed = 0

        for e in calendar:
            ne = storage.Schedule(team=e.team, rent=e.rent,
                                  room=e.room, status='0')

            if e.team is not None:
                object = e.team
            else:
                object = e.rent

            ne.duration = object.duration
            ne.begin_datetime = datetime.combine(week_start, e.time) + timedelta(days=int(e.day))
            ne.end_datetime = ne.begin_datetime + timedelta(minutes=(60 * object.duration)) - timedelta(seconds=1)

            # check for existent event
            if 0 == storage.Schedule.objects.filter(room=e.room,
                                                    begin_datetime=ne.begin_datetime,
                                                    end_datetime=ne.end_datetime).count():
                ne.save()
                # copy coaches info
                if e.team is not None:
                    for coach in e.team.coaches.all():
                        ne.coaches.add(coach)
                count_copied += 1
            else:
                count_passed += 1
        return {'copied': count_copied, 'passed': count_passed}

class GetVisitors(AjaxForm):
    """ Form acquires an event ID and returns the list of visitors. """
    event_id = forms.IntegerField()

    def clean_event_id(self):
        return self.check_obj_existence(storage.Schedule, 'event_id')

    def query(self, request=None):
        event_id = self.cleaned_data['event_id']
        event = storage.Schedule.objects.get(id=event_id)
        return event.get_visitors()

class AddResource(AjaxForm):
    INFLOW = '0'

    id = forms.CharField(max_length=4)
    count = forms.IntegerField()
    price = forms.FloatField()

    def save(self):
        res_type=self.cleaned_data['id']
        res_count=self.cleaned_data['count']
        res_price=self.cleaned_data['price']

        print 'Add resource'
        resource = storage.Flow(user=self.request.user, # see deco
                                action=self.INFLOW,
                                type=res_type,
                                count=res_count,
                                price=res_price,
                                total=float(res_price * res_count))
        resource.save()
        return resource.id

class SubResource(AjaxForm):
    OUTFLOW = '1'

    id = forms.CharField(max_length=4)
    count = forms.IntegerField()
    price = forms.FloatField()

    def save(self):
        res_type=self.cleaned_data['id']
        res_count=self.cleaned_data['count']
        res_price=self.cleaned_data['price']

        print 'Sub resource'
        resource = storage.Flow(user=self.request.user, # see deco
                                action=self.OUTFLOW,
                                type=res_type,
                                count=res_count,
                                price=res_price,
                                total=float(res_price * res_count))
        resource.save()
        return resource.id

# class StatusForm(forms.ModelForm):
#     change_flag = forms.BooleanField(required=False)
#     outside = forms.BooleanField(required=False)

#     class Meta:
#         model = storage.Schedule
#         exclude = ('room', 'team', 'begin')

#     def clean(self):
#         data = self.cleaned_data
#         if not data.get('change_flag', None):
#             if 'outside' in data:
#                 del data['outside']
#             if 'change' in data:
#                 del data['change']
#         elif not (data.get('change', False) or data.get('outside', False)):
#             raise forms.ValidationError('Set coach to change.')
#         elif data['outside']:
#             if 'change' in data:
#                 del data['change']
#         return data

#     def get_errors(self):
#         #FIXME: get_errors method is used in multiple forms(DRY)
#         from django.utils.encoding import force_unicode
#         return ''.join([force_unicode(v) for k, v in self.errors.items()])

# class ScheduleForm(forms.ModelForm):

#     class Meta:
#         model = storage.Schedule
#         exclude = ('change', 'status')

#     def clean_begin(self):
#         begin = self.cleaned_data['begin']
#         if begin < datetime.now():
#             raise forms.ValidationError('Can not create event in the past.')
#         return begin

#     def clean(self):
#         room = self.cleaned_data['room']
#         begin = self.cleaned_data.get('begin')
#         team = self.cleaned_data['team']

#         if room and begin and team:
#             end = begin + timedelta(hours=team.duration)
#             result = storage.Schedule.objects.select_related().filter(room=room).filter(begin__range=(begin.date(), begin.date()+timedelta(days=1)))

#             if self.instance.pk:
#                 result = result.exclude(pk=self.instance.pk)

#             for item in result:
#                 if (begin < item.end < end) or (begin <= item.begin < end):
#                     raise forms.ValidationError('Incorect begin date for this room')
#         return self.cleaned_data

#     def get_errors(self):
#         from django.utils.encoding import force_unicode
#         return ''.join([force_unicode(v) for k, v in self.errors.items()])

# class UserCardForm(forms.ModelForm):
#     rfid_code = forms.CharField(max_length=8)

#     class Meta:
#         model = storage.Card
#         exclude = ('reg_date', 'exp_date', 'client')

#     def clean_rfid_code(self):
#         rfid = self.cleaned_data['rfid_code']
#         try:
#             user = storage.Client.objects.get(rfid_code=rfid)
#             self.cleaned_data['client'] = user
#         except storage.Client.DoesNotExist:
#             raise form.ValidationError('Undefined rfid code.')
#         return user

#     def save(self, commit=True):
#         obj = super(UserCardForm, self).save(commit=False)
#         obj.client = self.cleaned_data['client']
#         obj.exp_date = datetime.now() + timedelta(days=30)
#         obj.save(commit)
#         return obj

#     def get_errors(self):
#         from django.utils.encoding import force_unicode
#         return ''.join([force_unicode(v) for k, v in self.errors.items()])

# class CopyForm(forms.Form):
#     from_date = forms.DateField()
#     to_date = forms.DateField()

#     def get_errors(self):
#         from django.utils.encoding import force_unicode
#         return ''.join([force_unicode(v) for k, v in self.errors.items()])

#     def validate_date(self, date):
#         if not date.weekday() ==  0:
#             raise forms.ValidationError('Date must be a Monday.')
#         return date

#     def clean_from_date(self):
#         return self.validate_date(self.cleaned_data['from_date'])

#     def clean_to_date(self):
#         to_date = self.validate_date(self.cleaned_data['to_date'])
#         if to_date < date.today():
#             raise forms.ValidationError('Can not paste events into the past.')
#         if storage.Schedule.objects.filter(begin__range=(to_date, to_date+timedelta(days=7))).count():
#             raise forms.ValidationError('Week must be empty to paste events.')
#         return to_date

#     def clean(self):
#         from_date = self.cleaned_data.get('from_date', None)
#         to_date = self.cleaned_data.get('to_date', None)
#         if from_date and to_date and from_date == to_date:
#             raise forms.ValidationError('Copy to the same week.')
#         return self.cleaned_data

#     def save(self):
#         from_date = self.cleaned_data.get('from_date')
#         to_date = self.cleaned_data.get('to_date')
#         events = storage.Schedule.objects.filter(begin__range=(from_date, from_date+timedelta(days=7)))
#         delta = to_date - from_date
#         for e in events:
#             ne = storage.Schedule(room=e.room, team=e.team)
#             ne.begin = e.begin+delta
#             ne.end = ne.begin + timedelta(minutes=int(60 * e.duration))
#             ne.duration = e.duration
#             ne.save()
