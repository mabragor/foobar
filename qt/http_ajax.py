# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import httplib, urllib, json

from dlg_settings import TabNetwork

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HttpAjax(QObject):

    def __init__(self, parent, url, params):
        self.get_settings()

        self.parent = parent

        params = urllib.urlencode(params)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        hostport = '%s:%s' % (self.host, self.port)
        print 'HttpAjax:', hostport
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
        if self.response.status == 200: # http status
            data = self.response.read()
            response = json.read(data)
            if 'code' in response and response['code'] != 200: # json status
                QMessageBox.warning(self.parent, _('Warning'),
                                    '[%(code)s] %(desc)s' % response,
                                    QMessageBox.Ok, QMessageBox.Ok)
                return None
            return response
        else:
            print self.response.status
            open('./dump.html', 'w').write(self.response.read())
            QMessageBox.critical(
                self.parent, _('HTTP Error'),
                '[%s] %s' % (
                    self.response.status,
                    self.response.reason
                    )
                )
            return None
