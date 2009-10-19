# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from lib.decorators import ajax_processor
from django.shortcuts import get_object_or_404
from lib import DatetimeJSONEncoder
from lib.decorators import render_to
from forms import ScheduleForm, UserRFID

from storage.models import Schedule, Room, Group, Client

#@render_to('manager/index.html')
@render_to('manager.html')
def index(request):
    form = ScheduleForm()
    return {
        'form': form,
        'options': simplejson.dumps(settings.CALENDAR_OPTIONS, cls=DatetimeJSONEncoder)
    }

@ajax_processor()
def ajax_get_rooms(request):
    rooms = Room.objects.all()
    return {'rows': [item.get_calendar_obj() for item in rooms]}

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
        event = Schedule.objects.get(pk=request.POST['id'])
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

