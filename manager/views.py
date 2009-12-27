# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from lib.decorators import ajax_processor
from django.shortcuts import get_object_or_404
from lib import DatetimeJSONEncoder
from lib.decorators import render_to
from forms import ScheduleForm, UserRFID, StatusForm, CopyForm, UserCardForm

from storage.models import Schedule, Room, Group, Client, Card, Coach

#@render_to('manager/index.html')
@render_to('manager.html')
def index(request):
    return {
        'options': simplejson.dumps(settings.CALENDAR_OPTIONS, cls=DatetimeJSONEncoder)
    }

@ajax_processor()
def ajax_get_rooms(request):
    rooms = Room.objects.all()
    return {'rows': [item.get_store_obj() for item in rooms]}

@ajax_processor()
def ajax_get_course_tree(request):
    groups = Group.objects.all()
    return [item.get_tree_node() for item in groups]

@ajax_processor(UserRFID)
def ajax_get_user_courses(request, form):
    rfid = form.cleaned_data['rfid_code']
    try:
        user = Client.objects.get(rfid_code=rfid)
        return {'courses': user.get_course_list()}
    except Client.DoesNotExist:
        return {'courses': []} # FIXME

@ajax_processor()
def ajax_add_event(request, pk=None):
    output = {}
    if request.method == 'POST':
        if request.POST.get('event_id', None):
            form = ScheduleForm(request.POST, instance=Schedule.objects.get(pk=request.POST.get('event_id')))
        else:
            form = ScheduleForm(request.POST)
        if form.is_valid():
            obj = form.save()
            output['success'] = True
            output['msg'] = 'Save succesfull'
            output['obj'] = obj.get_calendar_obj()
        else:
            output['success'] = False
            output['errors'] = form.get_errors()
    else:
        output['success'] = False
        output['errors'] = _(u'Incorrect request method.')
    return output

@ajax_processor()
def ajax_del_event(request):
    if request.method == 'POST':
        event = get_object_or_404(Schedule, pk=request.POST['id'])
        if event.begin < datetime.now():
            return {'error': 'Event was in the past.'}
        event.delete()
        return {}
    return {'error': 'Invalid request type.'}

@ajax_processor()
def ajax_change_date(request):
    if request.method == 'POST':
        event = get_object_or_404(Schedule, pk=request.POST['pk'])
        if event.begin < datetime.now():
            return {'result': False, 'msg': 'Cann\'t edit past event.'}
        begin = datetime.fromtimestamp(int(request.POST['start']))
        if begin < datetime.now():
            return {'result': False, 'msg': 'Cann\'t set event in the past.'}
        end = begin + timedelta(hours=event.course.duration),
        end = end[0]
        result = Schedule.objects.select_related().filter(room=event.room).filter(begin__day=begin.day).exclude(pk=event.pk)

        for item in result:
            if (begin < item.end < end) or (begin <= item.begin < end):
                return {'result': False, 'msg': 'Two events in the same room.'}
        event.begin = begin
        event.save()
        return {'result': True}
    return {'result': False, 'msg': 'Incorect request type.'}

@ajax_processor()
def ajax_get_events(request):
    if request.method == 'POST':
        start = datetime.fromtimestamp(int(request.POST['start']))
        end = datetime.fromtimestamp(int(request.POST['end']))
        schedules = Schedule.objects.filter(begin__range=(start, end))
        if 'rooms' in request.POST:
            schedules = schedules.filter(room__in=request.POST.getlist('rooms'))
        events = [item.get_calendar_obj() for item in schedules]
    else:
        events = []
    return events

@ajax_processor()
def ajax_del_user_couse(request):
    if request.method == 'POST':
        try:
            card = Card.objects.get(pk=request.POST.get('id'))
        except Card.DoesNotExist:
            return {'result': False, 'msg': 'Incorect course.'}
        if card.deleteable():
            card.delete()
            return {'result': True, 'msg': 'Success.'}
        else:
            return {'result': False, 'msg': 'Course is undeleteable.'}
    return {'result': False, 'msg': 'Incorect request type.'}

@ajax_processor()
def ajax_add_user_course(request):
    output = {}
    if request.method == 'POST':
        form = UserCardForm(request.POST)
        if form.is_valid():
            obj = form.save()
            output['success'] = True
            output['data'] = obj.get_info()
        else:
            output['success'] = False
            output['errors'] = form.get_errors()
    return output

@ajax_processor()
def ajax_get_coach_list(request):
    from django.db.models import Q
    coaches = Coach.objects.all()
    if 'query' in request.POST:
        coaches = coaches.filter(Q(first_name__icontains=request.POST.get('query'))|Q(last_name__icontains=request.POST.get('query')))
    return {'rows': [item.get_store_obj() for item in coaches]}

@ajax_processor()
def ajax_get_unstatus_event(request):
    event = Schedule.get_unstatus_event()
    if event:
        output = {
            'success': True,
            'data': event
        }
    else:
        output = {
            'success': False,
            'errors': 'There is not events without status.',
            'end': True
        }
    return output

@ajax_processor()
def ajax_save_event_status(request):
    output = {}
    if request.method == 'POST':
        try:
            event = Schedule.objects.get(pk=request.POST.get('id'), status__isnull=True)
            form = StatusForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                output['success'] = True
                output['msg'] = 'Saved success.'
            else:
                output['success'] = False
                output['errors'] = form.get_errors()
        except Schedule.DoesNotExist:
            output['success'] = True
            output['msg'] = 'Event has status.'
    return output

@ajax_processor()
def ajax_get_status_timer(request):

    def f(ph, cs):
        import time
        t = time.time() - cs*60
        slot_length = 60*60/ph
        dt = slot_length - (t % slot_length)
        return dt
    return f(settings.CALENDAR_OPTIONS['timeslotsPerHour'], settings.CHECK_STATUS_INTERVAL)

@ajax_processor()
def ajax_copy_week(request):
    output = {}
    if request.method == 'POST':
        form = CopyForm(request.POST)
        if form.is_valid():
            form.save()
            output['success'] = True
        else:
            output['success'] = False
            output['errors'] = form.get_errors()
    return output
