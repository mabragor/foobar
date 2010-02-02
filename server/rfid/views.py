# -*- coding: utf-8 -*-

import operator, random
from datetime import datetime, timedelta

from django.conf import settings

from lib.decorators import ajax_processor
from storage.models import Client
from rfid.forms import GetRfidCode
from rfid.models import Card

@ajax_processor(GetRfidCode)
def info_by_rfid(request, form):
    """
    This function returns user's information by its RFID card code.
    @return Client object
    """
    rfid = rfid_reader()
    try:
        user = Client.objects.get(rfid_code=rfid)
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'rfid_code': user.rfid_code
            }
    except Client.DoesNotExist:
        return {}

def rfid_reader():
    if False: #settings.DEBUG:
        codes = settings.DEMO_CODES
        index = random.randint(0, len(codes) - 1)
        return codes[index][:8]
    else:
        last_card = Card.objects.all().order_by('-reg_date')[0]
        if datetime.now() - timedelta(seconds=5) < last_card.reg_date:
            return last_card.code
        else:
            return '00000000'

def is_valid(rfid_response):
    """
    This function is used to validate the RFID reader response.
    @return: Boolean
    """
    code = rfid_response[:8]
    checksum = rfid_response[8]
    crc = '%X' % reduce(operator.xor, [ord(a) for a in tuple(code)])
    res = '%X' % reduce(operator.xor, [int(a,16) for a in tuple(crc)])
    return res == checksum

def code_checksum(rfid8):
    """
    This function is used to get checksum symbol for the rfid code.
    @return: String
    """
    crc = '%X' % reduce(operator.xor, [ord(a) for a in tuple(rfid8)])
    res = '%X' % reduce(operator.xor, [int(a,16) for a in tuple(crc)])
    return res

def generate():
    """
    This function generates demo RFID code.
    @return: String
    """
    symbols = tuple('0123456789ABCDEF')
    rfid_code = []
    for i in xrange(8):
        index = random.randint(0, len(symbols) - 1)
        rfid_code.append(symbols[index])
    rfid = ''.join(rfid_code)
    return '%(rfid)s%(checksum)s' % {
        'rfid': rfid,
        'checksum': code_checksum(rfid)
        }
