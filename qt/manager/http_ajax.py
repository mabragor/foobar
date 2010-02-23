# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import httplib, urllib, json, base64, string

from dlg_settings import TabNetwork

from settings import DEBUG

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HttpAjax(QObject):

    def __init__(self, parent, url, params, session_id=None):
        self.get_settings()

        self.parent = parent

        params = urllib.urlencode(params)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}

        if session_id:
            headers.update( { 'Cookie': 'sessionid=%s' % session_id } )

        hostport = '%s:%s' % (self.host, self.port)
        if DEBUG:
            print 'HttpAjax:', hostport, '\n', headers
        conn = httplib.HTTPConnection(hostport)
        conn.request('POST', url, params, headers)
        self.response = conn.getresponse()

        # sessionid=d5b2996237b9044ba98c5622d6311c43;
        # expires=Tue, 09-Feb-2010 16:32:24 GMT;
        # Max-Age=1209600;
        # Path=/

        cookie_string = self.response.getheader('set-cookie')
        if cookie_string:
            cookie = {}
            for item in cookie_string.split('; '):
                key, value = item.split('=')
                cookie.update( { key: value } )
            if DEBUG:
                import pprint
                pprint.pprint(cookie)

            session_id = cookie.get('sessionid', None)
            if DEBUG:
                print 'session id is', session_id
            self.parent.setSessionID(session_id)

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
        elif self.response.status == 302: # authentication
            QMessageBox.warning(self.parent, _('Warning'),
                                _('Authenticate yourself.'))
            return None
        elif self.response.status == 500: # error
            open('./dump.html', 'w').write(self.response.read())
        else:
            QMessageBox.critical(
                self.parent, _('HTTP Error'),
                '[%s] %s' % (
                    self.response.status,
                    self.response.reason
                    )
                )
            return None
