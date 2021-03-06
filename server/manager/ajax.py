# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required

from datetime import datetime, date, timedelta

from lib.decorators import ajax_processor, formset_processor

import forms
from storage import models as storage

from signals import signal_log_action

isJavaScript = False

def abstract_request(request, form):
    if form.is_valid():
        result = form.query(request)
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

def abstract_formset(request, formset):
    if formset.is_valid():
        for form in formset.forms:
            form.save()
    else:
        return {'code': 404, 'desc': 'Form is not valid',
                'errors': formset.errors}
    return {'code': 200, 'desc': 'Ok'}

@ajax_processor(forms.Login, isJavaScript)
def login(request, form):
    response, result = abstract_request(request, form)
    response.update( {'user_info': result} )
    signal_log_action.send(sender=None, action='login %s' % result)
    return response

@login_required
@ajax_processor(None, isJavaScript)
def static(request):
    data = {}

    params = (
        ('coaches', 'model', storage.Coach),
        ('card_ordinary', 'model', storage.CardOrdinary),
        ('card_club', 'model', storage.CardClub),
        ('card_promo', 'model', storage.CardPromo),
        ('price_cats_team', 'model', storage.PriceCategoryTeam),
        ('price_cats_rent', 'model', storage.PriceCategoryRent),
        ('discounts', 'model', storage.Discount),
        ('styles', 'model', storage.DanceStyle),
        ('event_fix_choice', 'tuple', storage.Schedule.EVENT_FIXED),
        )
    for key, _type, model in params:
        if _type == 'model':
            qs = model.objects.filter(is_active=True)
            data.update( {key: [item.about() for item in qs], } )
        elif _type == 'tuple':
            data.update( {key: model} )
        else:
            raise RuntimeWarning('STATIC')
    return data

@login_required
@ajax_processor(forms.UserSearch, isJavaScript)
def get_users_info_by_name(request, form):
    response, users = abstract_request(request, form)
    response.update( {'users': users} )
    return response

@login_required
@ajax_processor(forms.ClientInfo, isJavaScript)
def set_client_info(request, form):
    signal_log_action.send(sender=request.user, action='set_client_info')
    return abstract_response(request, form)

@login_required
@formset_processor(forms.ClientCard)
def set_client_card(request, formset):
    signal_log_action.send(sender=request.user, action='set_client_card')
    return abstract_formset(request, formset)

@login_required
@ajax_processor(forms.UserIdRfid, isJavaScript)
def get_client_info(request, form):
    response, info = abstract_request(request, form)
    response.update( {'info': info} )
    #import pprint; pprint.pprint(response)
    return response

@login_required
@ajax_processor(forms.PaymentAdd, isJavaScript)
def payment_add(request, form):
    signal_log_action.send(sender=request.user, action='payment_add')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.RenterInfo, isJavaScript)
def set_renter_info(request, form):
    signal_log_action.send(sender=request.user, action='set_renter_info')
    return abstract_response(request, form)

@login_required
@formset_processor(forms.RenterCard)
def set_renter_card(request, formset):
    signal_log_action.send(sender=request.user, action='set_renter_card')
    return abstract_formset(request, formset)

@login_required
@ajax_processor(forms.UserIdRfid, isJavaScript)
def get_renter_info(request, form):
    response, info = abstract_request(request, form)
    response.update( {'info': info} )
    return response

@login_required
@ajax_processor(forms.GetScheduleInfo, isJavaScript)
def get_event_info(request, form):
    response, result = abstract_request(request, form)
    response.update( {'info': result} )
    return response

@login_required
@ajax_processor(forms.DateRange, isJavaScript)
def get_week(request, form):
    response, events = abstract_request(request, form)
    response.update( {'events': events} )
    return response

@login_required
@ajax_processor(forms.FillWeek, isJavaScript)
def fill_week(request, form):
    signal_log_action.send(sender=request.user, action='fill_week')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.CopyWeek, isJavaScript)
def copy_week(request, form):
    signal_log_action.send(sender=request.user, action='copy_week')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.RegisterVisit, isJavaScript)
def register_visit(request, form):
    signal_log_action.send(sender=request.user, action='register_visit')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.RenterCard, isJavaScript)
def register_rent(request, form):
    signal_log_action.send(sender=request.user, action='register_rent')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.RegisterChange, isJavaScript)
def register_change(request, form):
    signal_log_action.send(sender=request.user, action='register_change')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.RegisterFix, isJavaScript)
def register_fix(request, form):
    signal_log_action.send(sender=request.user, action='register_fix')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.CalendarEventAdd, isJavaScript)
def cal_event_add(request, form):
    signal_log_action.send(sender=request.user, action='cal_event_add')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.CalendarEventDel, isJavaScript)
def cal_event_del(request, form):
    signal_log_action.send(sender=request.user, action='cal_event_del')
    return abstract_remove(request, form)

@login_required
@ajax_processor(forms.ExchangeRoom, isJavaScript)
def exchange_room(request, form):
    signal_log_action.send(sender=request.user, action='exchange_room')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.GetVisitors, isJavaScript)
def get_visitors(request, form):
    response, visitors = abstract_request(request, form)
    response.update( {'visitor_list': visitors} )
    return response

@login_required
@ajax_processor(None, isJavaScript)
def get_rents(request):
    #today = date.today()
    #end = today + timedelta(days=(7 - today.weekday()))
    #rents = storage.Rent.objects.filter(begin_date__range=(today, end))
    rents = storage.Rent.objects.filter(end_date__gte=date.today)
    rent_list = [i.about(True) for i in rents]
    return {'code': 200, 'desc': 'Ok', 'rent_list': rent_list}

@login_required
@ajax_processor(None, isJavaScript)
def get_coaches(request):
    coaches = storage.Coach.objects.all()
    coaches_list = [i.about() for i in coaches]
    return {'code': 200, 'desc': 'Ok', 'coaches_list': coaches_list}

@login_required
@ajax_processor(None, isJavaScript)
def get_accounting(request):
    accounting = storage.Accounting.objects.all()
    accounting_list = [i.about() for i in accounting]
    return {'code': 200, 'desc': 'Ok', 'accounting_list': accounting_list}

@login_required
@ajax_processor(forms.AddResource, isJavaScript)
def add_resource(request, form):
    signal_log_action.send(sender=request.user, action='add_resource')
    return abstract_response(request, form)

@login_required
@ajax_processor(forms.SubResource, isJavaScript)
def sub_resource(request, form):
    signal_log_action.send(sender=request.user, action='sub_resource')
    return abstract_response(request, form)

