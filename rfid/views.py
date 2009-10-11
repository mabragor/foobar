# -*- coding: utf-8 -*-

from lib.decorators import ajax_processor
from rfid.forms import GetRfidCode
from manager.models import Client

def rfid_reader(): # FIXME: real code to work with reader
    return '008365B0'

@ajax_processor(GetRfidCode)
def info_by_rfid(request, form):

    rfid = rfid_reader()
    user = Client.objects.get(rfid_code=rfid)

    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        }
