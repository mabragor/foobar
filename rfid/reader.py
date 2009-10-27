#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, serial, operator
from datetime import datetime, timedelta

PORT = {
    'name': '/dev/ttyUSB0',
    'rate': 38400,
    'bits_in_byte': 7,
    'parity': 'N',
    'stop_bits': 2
}

try:
    if sys.argv[1] == '-d':
        import daemonize
        daemonize.createDaemon()
except IndexError:
    pass

# Подключение и настройка среды Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('/home/rad/django.engine')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from rfid.models import Card
from django import db

import logging
logging.basicConfig(level=logging.DEBUG,
                    filename='/tmp/rfid.daemon.log', filemode='a')

class ReaderRFID:

    def __init__(self, port_settings):
        self.settings = port_settings
        self.port = serial.Serial(
            self.settings['name'], 
            self.settings['rate'],
            bytesize = self.settings['bits_in_byte'],
            parity = self.settings['parity'], 
            stopbits = self.settings['stop_bits']
            )
        self.port.setDTR(True)
        self.port.setRTS(True)

        logging.debug(
            'Open port %s with %s,%s,%s,%s' % (
                self.port.getPort(),
                self.port.getBaudrate(),
                self.port.getByteSize(),
                self.port.getParity(),
                self.port.getStopbits()
                )
            )

    def is_open(self):
        return self.port.isOpen()

    def close(self):
        self.port.close()

    def hex(self, symbol):
        return '%02X' % ord(symbol)

    def checksum(self, rfid8):
        """
        This function is used to get checksum symbol for the rfid code.
        @return: String
        """
        crc = '%X' % reduce(operator.xor, [ord(a) for a in tuple(rfid8)])
        res = '%X' % reduce(operator.xor, [int(a,16) for a in tuple(crc)])
        return res

    def wait(self):
        cache = { 'card': None, 'time': datetime.now() }
        period = timedelta(seconds=3)
        buffer = []
        while True:
            symbol = self.port.read(1)
            if not self.hex(symbol) == '0D':
                buffer.append(symbol)
            else:
                if '0A' == self.hex(self.port.read(1)):
                    if len(buffer) == 9:
                        # use cache if possible
                        if datetime.now() - period > cache['time']:
                            record = Card(code=''.join(buffer[1:]))
                            record.save()
                            cache.update( { 'card': buffer[1:], 'time': datetime.now() } )
                            if settings.DEBUG:
                                logging.debug(
                                    'RFID is %s \t Dump is %s \t Checksum is %s' % (
                                        ''.join(buffer), 
                                        ' '.join([self.hex(s) for s in buffer]),
                                        self.checksum(buffer[1:])
                                        )
                                    )
                        else:
                            if settings.DEBUG:
                                logging.debug('Use cache data.')
                    buffer = []

if __name__ == '__main__':
    try:
        reader = ReaderRFID(PORT)
        if reader.is_open():
            reader.wait()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        reader.close()

sys.exit(0)
