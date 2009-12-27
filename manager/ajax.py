# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404

from datetime import datetime, date, timedelta

from lib import str2date
from lib.decorators import ajax_processor, render_to

from forms import UserRFID, UserName, UserInfo, DateRange, CopyWeek

from storage.models import Client, Card, Course, Group, Schedule

isJavaScript = False

@ajax_processor(None, isJavaScript)
def available_courses(request):
    groups = Group.objects.all()
    return [item.get_node() for item in groups]

@ajax_processor(UserRFID, isJavaScript)
def get_user_info(request, form):
    rfid_id = form.cleaned_data['rfid_code']
    user = get_object_or_404(Client, rfid_code=rfid_id)
    return {
        'user_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'rfid_id': rfid_id,
        'reg_date': user.reg_date,
        'course_list': user.get_course_list()
        }

@ajax_processor(UserName, isJavaScript)
def get_users_info_by_name(request, form):
    name = form.cleaned_data['name']
    user_list = Client.objects.filter(Q(first_name=name)|Q(last_name=name))
    result = [(user.last_name, user.first_name, user.rfid_code) for user in user_list]
    print result
    return {'code': 200, 'desc': 'Ok',
            'user_list': result,
            }

@ajax_processor(UserInfo, isJavaScript)
def set_user_info(request, form):
    data = form.cleaned_data
    user_id = data['user_id']; del(data['user_id'])
    # save common data
    if 0 == int(user_id):
        user = Client(**data)
    else:
        user = Client.objects.get(id=user_id)
        for key, value in data.items():
            setattr(user, key, value)
    user.save()
    # assigned courses
    assigned = data['course_assigned']
    if len(assigned) > 0:
        for id, card_type, bgn_date in assigned:
            bgn_date = date(*[int(i) for i in bgn_date.split('-')])
            course = Course.objects.get(id=id)
            card = Card(course=course, client=user,type=card_type,
                        bgn_date=bgn_date,
                        exp_date=bgn_date + timedelta(days=30),
                        count_sold=course.count,
                        price=course.price)
            card.save()

    return {'code': 200, 'desc': 'Ok'}

@ajax_processor(DateRange, isJavaScript)
def get_week(request, form):
    c = form.cleaned_data
    schedules = Schedule.objects.filter(begin__range=(c['monday'], c['sunday']))
    if len(c['filter']) > 0:
        schedules = schedules.filter(room__in=c['filter'])
    events = [item.get_calendar_obj() for item in schedules]
    return {'code': 200, 'desc': 'Ok', 'events': events}

@ajax_processor(CopyWeek, isJavaScript)
def copy_week(request, form):
    c = form.cleaned_data
    if form.is_valid():
        form.save()
    else:
        return {'code': 404, 'desc': 'Form is not valid',
                'errors': form.get_errors()}
    return {'code': 200, 'desc': 'Ok'}
