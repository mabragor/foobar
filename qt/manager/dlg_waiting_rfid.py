# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import serial, random, time

from os.path import dirname, join

from settings import _, DEBUG, PORT

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
                     self.reject)

        self.reader.start()

    def done(self, result_code):
        QDialog.done(self, result_code)
        # Send the kill event to RFID reader thread.
        self.reader.timeToDie()

    def closeEvent(self, event):
        self.accept()
        event.accept()

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
        self.die = True

    def hex(self, symbol):
        return '%02X' % ord(symbol)

    def dispose(self):
        if not self.disposed:
            self.disposed = True
            # close the port
            self.port.setDTR(False)
            self.port.setRTS(False)
            self.port.close()

    def run(self):
        if DEBUG:
            # debug part, in case of absence of the RFID reader
            print 'debugging part of code, in case of RFID '\
                'reader absence. See rfid.py\'s DEBUG variable.'
            demo_rfids = ['008365B0', ]#'0083AD33', '00836012']
            index = random.randint(0, len(demo_rfids) - 1)
            rfid_code = demo_rfids[index]
            time.sleep(1)
            self.callback(rfid_code)
            QCoreApplication.postEvent(self.dialog, QCloseEvent())
            return

        rfid_code = ''
        # init the reader
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
        # the infinite loop until get the card id
        # format is =012345678<OD><OA>
        while True:
            symbol = self.port.read(1)
            if not self.hex(symbol) == '0D':
                buffer.append(symbol)
            else:
                if '0A' == self.hex(self.port.read(1)):
                    if len(buffer) == 9:
                        # skip the first symbol
                        rfid_code = ''.join(buffer[1:])
                        break
                    # in any cases buffer has to be clean, because of
                    # it contains of old id or test symbol.
                    buffer = []

                    # user closes the dialog, kill the reader's thread
                    if self.die:
                        break

        if not self.die:
            # Send the card's id
            self.callback(rfid_code)
            # Close the dialog's window
            QCoreApplication.postEvent(self.dialog, QCloseEvent())

        self.dispose()
