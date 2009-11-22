# -*- coding: utf-8 -*-
from lib.decorators import render_to, ajax_processor
from storage.models import Schedule, Room, Group, Client, Card, Coach
from datetime import datetime, timedelta
from client import forms

@render_to('client1.html')
def index(request):
    return {
    }

@ajax_processor(forms.ActiveCourses)
def get_active_courses(request, form):
    rfid = form.cleaned_data['rfid_code']
    today = datetime.today()
    schedule = Schedule.objects.filter(begin__range=(today.date(), today.date()+timedelta(days=1))).order_by('-begin')
    try:
        user = Client.objects.get(rfid_code=rfid)
    except Client.DoesNotExist:
        user = None
    output = []
    for item in schedule:
        print item
        output.append(item.get_for_user(user))
    return {'courses': output}
