# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from lib.decorators import ajax_processor, render_to

from forms import UserRFID

from storage.models import Client

isJavaScript = False

@ajax_processor(UserRFID, isJavaScript)
def user_info(request, form):
    rfid = form.cleaned_data['rfid_code']
    user = get_object_or_404(Client, rfid_code=rfid)
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'reg_date': user.reg_date,
        'course_list': user.get_course_list()
        }
