#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import serial, random, time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

DEBUG = False
PORT = {
    'name': '/dev/ttyUSB0',
    'rate': 38400,
    'bits_in_byte': 7,
    'parity': 'N',
    'stop_bits': 2
    }

class WaitingRFID(QThread):
    def __init__(self, parent):
        self.dialog = parent.dialog
        self.callback = parent.callback

        self.disposed = False
        self.die = False

        QThread.__init__(self)

    def __del__(self):
        self.dispose()

    def timeToDie(self):
        print 'thread prepare to die'
        self.die = True

    def hex(self, symbol):
        return '%02X' % ord(symbol)

    def dispose(self):
        print 'dispose'
        if not self.disposed:
            self.disposed = True
            # закрываем порт
            self.port.setDTR(False)
            self.port.setRTS(False)
            self.port.close()

    def run(self):
        if DEBUG:
            # отладочный код, на случай отсутствия считывателя
            demo_rfids = ['008365B0', '0083AD33', '00836012']
            index = random.randint(0, len(demo_rfids) - 1)
            rfid_code = demo_rfids[index]
            time.sleep(3)
            self.callback(rfid_code)
            QCoreApplication.postEvent(self.dialog, QCloseEvent())

        rfid_code = ''
        # инициализация считывателя
        self.port = serial.Serial(PORT['name'], PORT['rate'],
                                  bytesize = PORT['bits_in_byte'],
                                  parity = PORT['parity'],
                                  stopbits = PORT['stop_bits']
                             )
        self.port.setDTR(True)
        self.port.setRTS(True)

        buffer = []
        # бесконечный цикл, пока не получим идентификатор карты
        # формат: =012345678<OD><OA>
        while True:
            symbol = self.port.read(1)
            if not self.hex(symbol) == '0D':
                buffer.append(symbol)
            else:
                if '0A' == self.hex(self.port.read(1)):
                    if len(buffer) == 9:
                        # первый символ нам не нужен
                        rfid_code = ''.join(buffer[1:])
                        break
                    # в любом случае буфер надо чистить, так как в нём
                    # либо уже ненужный идентификатор, либо тестовый
                    # символ
                    buffer = []

                    # пользователь закрыл диалог, надо завершить поток
                    if self.die:
                        break

        if not self.die:
            # передаём код
            self.callback(rfid_code)
            # закрываем окно диалога
            QCoreApplication.postEvent(self.dialog, QCloseEvent())

        self.dispose()
