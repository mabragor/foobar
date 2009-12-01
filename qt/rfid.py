#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import serial

from PyQt4.QtCore import *
from PyQt4.QtGui import *

PORT = {
    'name': '/dev/ttyUSB0',
    'rate': 38400,
    'bits_in_byte': 7,
    'parity': 'N',
    'stop_bits': 2
    }

rfid_code = ''

class WaitingRFID(QThread):
    def __init__(self, parent):
        self.dialog = parent.dlg
        self.callback = parent.callback
        self.mutex = parent.rfidMutex
        self.condition = parent.rfidReader

        QThread.__init__(self)

    def hex(self, symbol):
        return '%02X' % ord(symbol)

    def run(self):
        port = serial.Serial(PORT['name'], PORT['rate'],
                             bytesize = PORT['bits_in_byte'],
                             parity = PORT['parity'],
                             stopbits = PORT['stop_bits']
                             )
        port.setDTR(True)
        port.setRTS(True)

        self.mutex.lock()
        print 'lock'
        self.condition.wait(self.mutex)
        print 'condition'

        buffer = []
        while True:
            symbol = port.read(1)
            #print symbol
            if not self.hex(symbol) == '0D':
                buffer.append(symbol)
            else:
                if '0A' == self.hex(port.read(1)):
                    if len(buffer) == 9:
                        rfid_code = ''.join(buffer[1:]) # see manager.py
                        break
                    buffer = []
        #print rfid_code
        self.callback(rfid_code)
        self.mutex.unlock()

        QCoreApplication.postEvent(self.dialog, QCloseEvent())

        port.close()
