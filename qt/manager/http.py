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
        self.headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
            }
        self.connect()

    def __del__(self):
        # close server's connection
        self.disconnect()

    def debug(self, message):
        if DEBUG:
            print '%s: %s' % (__name__, message)

    def connect(self):
        (self.host, self.port) = self.get_settings()
        self.hostport = '%s:%s' % (self.host, self.port)
        self.debug('Connect to %s\n%s' % (self.hostport, self.headers))
        self.conn = httplib.HTTPConnection(self.hostport)

    def disconnect(self):
        self.debug('Disconnect')
        self.conn.close()

    def reconnect(self):
        self.disconnect()
        self.connect()

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
                self.reconnect()
            except Exception, e:
                self.error_msg = '[%s] %s' % (e.errno, e.strerror.decode('utf-8'))
                self.response = None
                return False

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
            self.debug('session id is %s' % self.session_id)
        return True

    def parse(self, default={}): # public
        if not self.response: # request failed
            return None
        if self.response.status == 200: # http status
            data = self.response.read()
            if hasattr(json, 'read'):
                response = json.read(data) # 2.5
            else:
                response = json.loads(data) # 2.6
            if 'code' in response and response['code'] != 200:
                self.error_msg = '[%(code)s] %(desc)s' % response
                return default
            return response
        elif self.response.status == 302: # authentication
            self.error_msg = _('Authenticate yourself.')
            return default
        elif self.response.status == 500: # error
            self.error_msg = _('Error 500. Check dump!')
            open('./dump.html', 'w').write(self.response.read())
        else:
            self.error_msg = '[%s] %s' % (self.response.status, self.response.reason)
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
        is_success = http.request('/manager/get_rooms/', {})
        if is_success:
            result = http.parse()
            if 'rows' in result:
                print 'anonymous request: test passed'
        else:
            print http.error_msg

        # authenticate test user
        is_success = http.request('/manager/login/', TEST_CREDENTIALS)
        if is_success:
            result = http.parse()
            if 'code' in result and result['code'] == 200:
                print 'authenticate user: test passed'
        else:
            print http.error_msg

        # make autorized request
        from datetime import date
        params = {'to_date': date(2010, 5, 10)}
        is_success = http.request('/manager/fill_week/', params)
        if is_success:
            result = http.parse()
            if 'code' in result and result['code'] == 200:
                print 'authorized request: test passed'
        else:
            print http.error_msg

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(0)
