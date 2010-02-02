#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, serial, operator

port = serial.Serial('/dev/ttyUSB0', 38400, bytesize=7, parity='N', stopbits=2)
port.setDTR(True)
port.setRTS(True)

print 'Open port %s with %s,%s,%s,%s' % (
    port.getPort(),
    port.getBaudrate(),
    port.getByteSize(),
    port.getParity(),
    port.getStopbits()
)

print 'Is the port open:', port.isOpen()

def hex(symbol):
    return '%02X' % ord(symbol)

def code_checksum(rfid8):
    """
    This function is used to get checksum symbol for the rfid code.
    @return: String
    """
    crc = '%X' % reduce(operator.xor, [ord(a) for a in tuple(rfid8)])
    res = '%X' % reduce(operator.xor, [int(a,16) for a in tuple(crc)])
    return res

buffer = []
while True:
    symbol = port.read(1)
    if not hex(symbol) == '0D':
        buffer.append(symbol)
    else:
        if '0A' == hex(port.read(1)):
            if len(buffer) == 9:
                print 'RFID is %s \t Dump is %s \t Checksum is %s' % (
                    ''.join(buffer), 
                    ' '.join([hex(s) for s in buffer]),
                    code_checksum(buffer[1:])
                    )
            buffer = []
        else:
            print 'shit'
