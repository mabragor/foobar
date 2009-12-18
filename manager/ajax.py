# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from datetime import timedelta

from lib import str2date
from lib.decorators import ajax_processor, render_to

from forms import UserRFID, UserInfo

from storage.models import Client, Card, Course, Group

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
        for id, bgn_date in assigned:
            course = Course.objects.get(id=id)
            bgn_date = str2date(bgn_date)
            card = Card(course=course, client=user,type=1,
                        bgn_date=bgn_date,
                        exp_date=bgn_date + timedelta(days=30),
                        count_sold=course.count,
                        price=course.price)
            card.save()

    return {'code': 200, 'desc': 'Ok'}
