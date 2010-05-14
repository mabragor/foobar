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
        hostport = '%s:%s' % (self.host, self.port)
        if DEBUG:
            print 'Http:', hostport, '\n', headers

        # open connection to server
        self.conn = httplib.HTTPConnection(hostport)

    def __del__(self):
        # close server's connection
        self.conn.close()

    def get_settings(self): # private
        """ Use this method to obtain application's network settings. """
        self.settings = QSettings()

        network = TabNetwork()
        network.loadSettings(self.settings)

        host = network.addressHttpServer.text()
        port = network.portHttpServer.text()

        return (host, port)

    def request(self, url, params):
        if self.session_id and self.session_id not in self.headers:
            self.headers.update( { 'Cookie': 'sessionid=%s' % self.session_id } )

        params = urllib.urlencode(params)
        self.conn.request('POST', url, params, self.headers)
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

    def parse(self):
        if self.response.status == 200: # http status
            data = self.response.read()
            response = json.read(data)
            if 'code' in response and response['code'] != 200:
                msg = '[%(code)s] %(desc)s' % response
                if self.parent:
                    QMessageBox.warning(self.parent, _('Warning'), msg)
                else:
                    print msg
                return None
            return response
        elif self.response.status == 302: # authentication
            msg = _('Authenticate yourself.')
            if self.parent:
                QMessageBox.warning(self.parent, _('Warning'), msg)
            else:
                print msg
            return None
        elif self.response.status == 500: # error
            open('./dump.html', 'w').write(self.response.read())
        else:
            msg = '[%s] %s' % (self.response.status, self.response.reason)
            if self.parent:
                QMessageBox.critical(self.parent, _('HTTP Error'), msg)
            else:
                print msg
            return None

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
