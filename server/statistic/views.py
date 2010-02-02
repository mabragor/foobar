# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from lib.decorators import render_to
from storage.models import Course, Action, Schedule
from django.db.models import Count
from datetime import datetime, timedelta
from forms import MonthForm
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
    d = datetime.today()
    if request.method == 'POST':
        form = MonthForm(request.POST, start_year=d.year-2)
        if form.is_valid():
            d = form.cleaned_data['month']
    else:
         form = MonthForm(start_year=d.year-2)               
    for item in courses:
        rows.append(_get_row(item, d))
    
    return {
        'rows': rows,
        'date': d,
        'form': form
    }
    
def _get_row(item, d):
    row = []
    row.append(item.title)
    row.append(item.price * item.count)
    row.append(item.count)
    row.append(item.count * item.duration)
    r = Action.objects.filter(schedule__begin__year=d.year, schedule__begin__month=d.month)\
        .filter(schedule__status=1)\
        .filter(schedule__course=item)\
        .aggregate(Count('pk'))
    row.append(r['pk__count'])
    row.append('?')
    row.append(item.salary)
    row.append(item.price * item.count - item.salary)
    return row