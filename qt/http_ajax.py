#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import httplib, urllib, json

from dlg_settings import TabNetwork

from PyQt4.QtCore import *

class HttpAjax(QObject):

    def __init__(self, url, params):
        self.get_settings()

        params = urllib.urlencode(params)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        hostport = '%s:%s' % (self.host, self.port)
        print hostport
        conn = httplib.HTTPConnection(hostport)
        conn.request('POST', url, params, headers)
        self.response = conn.getresponse()
        conn.close()

    def get_settings(self):
        self.settings = QSettings()

        network = TabNetwork()
        network.loadSettings(self.settings)

        self.host = network.addressHttpServer.text()
        self.port = network.portHttpServer.text()

    def parse_json(self):
        if self.response.status == 200:
            data = self.response.read()
            return json.read(data)
        else:
            print 'HTTP Error is [%s] %s' % (
                self.response.status,
                self.response.reason
                )
            return None

