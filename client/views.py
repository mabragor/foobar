# -*- coding: utf-8 -*-
from lib.decorators import render_to
from forms import ScheduleForm
from django.conf import settings
from lib import DatetimeJSONEncoder
from django.utils import simplejson
from models import Schedule, Course, Room
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

@render_to('client/index.html')
def index(request):
    form = ScheduleForm()
    return {
        'form': form,
        'options': simplejson.dumps(settings.CALENDAR_OPTIONS, cls=DatetimeJSONEncoder)
    }

def ajax_add_event(request, pk=None):
    output = {}
    if request.method == 'POST':
        if pk:
            event = Schedule.objects.get(pk=pk)
            form = ScheduleForm(request.POST, instance=event)
        else:
            form = ScheduleForm(request.POST)
        if form.is_valid():
            obj = form.save()
            output['obj'] = obj.get_calendar_obj()
        else:
            output['error'] = u'Form isn\'t valid.'
    else:
        output['error'] = u'Incorect request method.'
    return HttpResponse(simplejson.dumps(output, cls=DatetimeJSONEncoder))

def ajax_del_event(request):
    if request.method == 'POST':
        Schedule.objects.get(pk=request.POST['id']).delete()
    return HttpResponse('{}')

def ajax_change_date(request):
    if request.method == 'POST':
        event = Schedule.objects.get(pk=request.POST['pk'])
        event.begin = datetime.fromtimestamp(int(request.POST['start']))
        event.save()
    return HttpResponse('{}')

def ajax_get_events(request):
    if request.method == 'POST':
        start = datetime.fromtimestamp(int(request.POST['start']))
        end = datetime.fromtimestamp(int(request.POST['end']))
        schedules = Schedule.objects.filter(begin__range=(start, end))
        events = [item.get_calendar_obj() for item in schedules]
    else:
        events = []
    return HttpResponse(simplejson.dumps(events, cls=DatetimeJSONEncoder))