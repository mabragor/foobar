#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import httplib, urllib, json

from PyQt4.QtCore import *

class HttpAjax(QObject):

    def __init__(self, host, port, url):
        params = urllib.urlencode({})
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        conn = httplib.HTTPConnection('%s:%s' % (host, port))
        conn.request('POST', url, params, headers)
        self.response = conn.getresponse()
        conn.close()

    def parse_json(self):
        if self.response.status == 200:
            data = self.response.read()
            return json.read(data)
        else:
            return None

