# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404

from datetime import datetime, date, timedelta

from lib import str2date
from lib.decorators import ajax_processor, render_to

import forms
from storage import models as storage

isJavaScript = False

@ajax_processor(None, isJavaScript)
def available_courses(request):
    groups = storage.Group.objects.all()
    return [item.about() for item in groups]

@ajax_processor(forms.UserRFID, isJavaScript)
def get_user_info(request, form):
    rfid_id = form.cleaned_data['rfid_code']
    user = get_object_or_404(storage.Client, rfid_code=rfid_id)
    return {
        'user_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'rfid_id': rfid_id,
        'reg_date': user.reg_date,
        'course_list': user.course_list()
        }

@ajax_processor(forms.UserName, isJavaScript)
def get_users_info_by_name(request, form):
    name = form.cleaned_data['name']
    user_list = storage.Client.objects.filter(Q(first_name=name)|Q(last_name=name))
    result = [(user.last_name, user.first_name, user.rfid_code) for user in user_list]
    print result
    return {'code': 200, 'desc': 'Ok',
            'user_list': result,
            }

@ajax_processor(forms.UserInfo, isJavaScript)
def set_user_info(request, form):
    data = form.cleaned_data
    user_id = data['user_id']; del(data['user_id'])
    # save common data
    if 0 == int(user_id):
        user = storage.Client(**data)
    else:
        user = storage.Client.objects.get(id=user_id)
        for key, value in data.items():
            setattr(user, key, value)
    user.save()
    # assigned courses
    assigned = data['course_assigned']
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

    return {'code': 200, 'desc': 'Ok'}

def abstract_request(request, form):
    if form.is_valid():
        result = form.query()
    else:
        return {'code': 404, 'desc': 'Form is not valid',
                'errors': form.get_errors()}
    return ({'code': 200, 'desc': 'Ok'}, result)

def abstract_response(request, form):
    if form.is_valid():
        id = form.save()
    else:
        return {'code': 404, 'desc': 'Form is not valid',
                'errors': form.get_errors()}
    return {'code': 200, 'desc': 'Ok', 'saved_id': id}

def abstract_remove(request, form):
    if form.is_valid():
        form.remove()
    else:
        return {'code': 404, 'desc': 'Form is not valid',
                'errors': form.get_errors()}
    return {'code': 200, 'desc': 'Ok'}

@ajax_processor(forms.GetScheduleInfo, isJavaScript)
def get_event_info(request, form):
    response, result = abstract_request(request, form)
    response.update( {'info': result} )
    return response

@ajax_processor(forms.DateRange, isJavaScript)
def get_week(request, form):
    response, events = abstract_request(request, form)
    response.update( {'events': events} )
    return response

@ajax_processor(forms.CopyWeek, isJavaScript)
def copy_week(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.RegisterVisit, isJavaScript)
def register_visit(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.CalendarEventAdd, isJavaScript)
def cal_event_add(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.CalendarEventDel, isJavaScript)
def cal_event_del(request, form):
    return abstract_remove(request, form)

@ajax_processor(forms.GetVisitors, isJavaScript)
def get_visitors(request, form):
    response, visitors = abstract_request(request, form)
    response.update( {'visitor_list': visitors} )
    return response

@ajax_processor(None, isJavaScript)
def get_rents(request):
    today = date.today()
    end = today + timedelta(days=(7 - today.weekday()))
    print today, end
    rents = storage.Rent.objects.filter(begin_date__range=(today, end))
    rent_list = [i.about() for i in rents]
    return {'code': 200, 'desc': 'Ok', 'rent_list': rent_list}
