# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import serial, random, time

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from settings import DEBUG, PORT

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgWaitingRFID(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.parent.dialog = self
        self.reader = WaitingRFID(self.parent)

        self.layout = QVBoxLayout()

        self.label = QLabel(_('Put the RFID label on to the RFID reader, please.'))
        self.layout.addWidget(self.label)

        self.cancel = QPushButton(_('Cancel'), self)
        self.layout.addWidget(self.cancel)

        self.setLayout(self.layout)
        self.setWindowTitle(_('RFID reader'))

        self.connect(self.cancel, SIGNAL('clicked()'),
                     self.unlink)
        self.reader.start()

    def closeEvent(self, event):
        self.accept()
        event.accept()

    def unlink(self):
        #Посылаем потоку RFID считывателя команду тихо завершиться.
        self.reader.timeToDie()
        # закрываем диалог
        self.reject()

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
            print 'debugging part of code, in case of RFID '\
                'reader absence. See rfid.py\'s DEBUG variable.'
            demo_rfids = ['008365B0', '0083AD33', '00836012']
            index = random.randint(0, len(demo_rfids) - 1)
            rfid_code = demo_rfids[index]
            time.sleep(1)
            self.callback(rfid_code)
            QCoreApplication.postEvent(self.dialog, QCloseEvent())
            return

        rfid_code = ''
        # инициализация считывателя
        try:
            self.port = serial.Serial(PORT['name'], PORT['rate'],
                                      bytesize = PORT['bits_in_byte'],
                                      parity = PORT['parity'],
                                      stopbits = PORT['stop_bits'])
        except serial.serialutil.SerialException:
            return

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
