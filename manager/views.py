# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from lib import DatetimeJSONEncoder
from lib.decorators import render_to
from forms import ScheduleForm

from storage.models import Schedule, Course, Room

#@render_to('manager/index.html')
@render_to('manager.html')
def index(request):
    form = ScheduleForm()

    return {
        'form': form,
        'options': simplejson.dumps(settings.CALENDAR_OPTIONS, cls=DatetimeJSONEncoder)
    }

def ajax_get_course_tree(request):
    courses = Course.objects.all()
    return HttpResponse(simplejson.dumps([item.get_tree_node() for item in courses], cls=DatetimeJSONEncoder))

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
        output['error'] = _(u'Incorrect request method.')
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
        if 'rooms' in request.POST:
            schedules = schedules.filter(room__in=request.POST['rooms'])
        events = [item.get_calendar_obj() for item in schedules]
    else:
        events = []
    return HttpResponse(simplejson.dumps(events, cls=DatetimeJSONEncoder))

