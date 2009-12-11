# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from lib.decorators import render_to
from storage.models import Course, Action, Schedule
from django.db.models import Count
from datetime import datetime, timedelta
import calendar

@render_to("statistic/index.html")
@staff_member_required
def index(request):
    return {}

@render_to("statistic/courses.html")
@staff_member_required
def courses(request):
    courses = Course.objects.all()
    rows = []
    today = datetime.today()
    start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=calendar.monthrange(start.year, start.day)[1])

    for item in courses:
        rows.append(_get_row(item, start, end))
    
    return {
        'rows': rows
    }
    
def _get_row(item, start, end):
    row = []
    row.append(item.title)
    row.append(item.price * item.count)
    row.append(item.count)
    row.append(item.count * item.duration)
    r = Action.objects.filter(schedule__begin__range=(start, end))\
        .filter(schedule__status=1)\
        .filter(schedule__course=item)\
        .aggregate(Count('pk'))
    row.append(r['pk__count'])
    row.append('?')
    row.append(item.salary)
    row.append(item.price * item.count - item.salary)
    return row