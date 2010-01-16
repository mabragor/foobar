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

@ajax_processor(None, isJavaScript)
def available_courses(request): #TODO!
#     response, users = abstract_request(request, form)
#     response.update( {'users': users} )
#     return response
    groups = storage.Group.objects.all()
    return [item.about() for item in groups]

@ajax_processor(forms.UserSearch, isJavaScript)
def get_users_info_by_name(request, form):
    response, users = abstract_request(request, form)
    response.update( {'users': users} )
    return response

@ajax_processor(forms.ClientInfo, isJavaScript)
def set_user_info(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.UserIdRfid, isJavaScript)
def get_client_info(request, form):
    response, info = abstract_request(request, form)
    response.update( {'info': info} )
    return response

@ajax_processor(forms.RenterInfo, isJavaScript)
def set_renter_info(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.RegisterRent, isJavaScript)
def set_rent(request, form):
    return abstract_response(request, form)

@ajax_processor(forms.UserIdRfid, isJavaScript)
def get_renter_info(request, form):
    response, info = abstract_request(request, form)
    response.update( {'info': info} )
    return response

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

@ajax_processor(forms.RegisterRent, isJavaScript)
def register_rent(request, form):
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
    rents = storage.Rent.objects.filter(begin_date__range=(today, end))
    rent_list = [i.about() for i in rents]
    return {'code': 200, 'desc': 'Ok', 'rent_list': rent_list}
