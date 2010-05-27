# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, httplib, urllib, json

from settings import _, DEBUG, TEST_CREDENTIALS
from dlg_settings import TabNetwork

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Http:

    def __init__(self, parent=None):
        self.session_id = None
        self.parent = parent
        self.headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        (self.host, self.port) = self.get_settings()
        self.hostport = '%s:%s' % (self.host, self.port)
        if DEBUG:
            print 'Http:', self.hostport, '\n', self.headers

        self.connect()

    def __del__(self):
        # close server's connection
        self.conn.close()

    def connect(self):
        self.conn = httplib.HTTPConnection(self.hostport)

    def is_session_open(self):
        return self.session_id is not None

    def get_settings(self): # private
        """ Use this method to obtain application's network settings. """
        self.settings = QSettings()

        network = TabNetwork()
        network.loadSettings(self.settings)

        host = network.addressHttpServer.text()
        port = network.portHttpServer.text()

        return (host, port)

    def request(self, url, params): # public
        if self.session_id and self.session_id not in self.headers:
            self.headers.update( { 'Cookie': 'sessionid=%s' % self.session_id } )

        params = urllib.urlencode(params)
        while True:
            try:
                self.conn.request('POST', url, params, self.headers)
                break
            except httplib.CannotSendRequest:
                print 'reconnect'
                self.connect()

        self.response = self.conn.getresponse()

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

            self.session_id = cookie.get('sessionid', None)
            if DEBUG:
                print 'session id is', self.session_id

    def parse(self, default={}): # public
        if self.response.status == 200: # http status
            data = self.response.read()
            if hasattr(json, 'read'):
                response = json.read(data) # 2.5
            else:
                response = json.loads(data) # 2.6
            if 'code' in response and response['code'] != 200:
                msg = '[%(code)s] %(desc)s' % response
                if self.parent:
                    QMessageBox.warning(self.parent, _('Warning'), msg)
                else:
                    print msg
                return default
            return response
        elif self.response.status == 302: # authentication
            msg = _('Authenticate yourself.')
            if self.parent:
                QMessageBox.warning(self.parent, _('Warning'), msg)
            else:
                print msg
            return default
        elif self.response.status == 500: # error
            open('./dump.html', 'w').write(self.response.read())
        else:
            msg = '[%s] %s' % (self.response.status, self.response.reason)
            if self.parent:
                QMessageBox.critical(self.parent, _('HTTP Error'), msg)
            else:
                print msg
            return default

# Test part of module

class TestWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.test()

    def test(self):
        # instantiate class object
        http = Http()

        # make anonimous request
        http.request('/manager/get_rooms/', {})
        result = http.parse()
        if 'rows' in result:
            print 'anonymous request: test passed'

        # authenticate test user
        http.request('/manager/login/', TEST_CREDENTIALS)
        result = http.parse()
        if 'code' in result and result['code'] == 200:
            print 'authenticate user: test passed'

        # make autorized request
        from datetime import date
        params = {'to_date': date(2010, 5, 10)}
        http.request('/manager/fill_week/', params)
        result = http.parse()
        if 'code' in result and result['code'] == 200:
            print 'authorized request: test passed'

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(0)
