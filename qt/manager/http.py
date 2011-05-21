# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, httplib, urllib, json

from settings import _, DEBUG, TEST_CREDENTIALS
from dlg_settings import TabNetwork

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Http:
    '''
    Implements interaction with server side of application.
    
    Upon L{instantiation<__init__>}, L{connects<connect>} to server and
    L{disconnects<disconnect>} upon L{destruction<__del__>}.
    
    Use L{request} method to request something from server. Response then
    should be analyzed with help of L{parse} method.
    '''
    
    def __init__(self, parent=None):
        '''
        Establishes connection to server upon instantiation, using L{connect}
        method.
        
        @type  session_id: string
        @param session_id: Identificator of session with the server. The only
        thing that persists between consecutive http requests.
        @type  parent: some class
        @param parent: Specifies parent class of this class. Parent class is
        the class where one of the attributes is an instance of this class, not
        to be confused with ancestor class.
        @type  headers: dict
        @param headers: Various parameters, common to all requests to server.
        '''
        self.session_id = None
        self.parent = parent
        self.headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'
            }
        self.connect()

    def __del__(self):
        '''
        On destruction of instance, closes connection to server.
        '''
        self.disconnect()

    def debug(self, message):
        '''
        Prints out various debug info, if DEBUG global variable is set to True.
        '''
        if DEBUG:
            print '%s: %s' % (__name__, message)

    def connect(self):
        '''
        Makes a connection to server.
        
        Uses L{get_settings} method to obtain network settings. If DEBUG global
        variable is set to True, prints out (host, port) and headers.
        '''
        
        (self.host, self.port) = self.get_settings()
        self.hostport = '%s:%s' % (self.host, self.port)
        self.debug('Connect to %s\n%s' % (self.hostport, self.headers))
        self.conn = httplib.HTTPConnection(self.hostport)

    def disconnect(self):
        '''
        Disconnects from the server.
        '''
        
        self.debug('Disconnect')
        self.conn.close()

    def reconnect(self):
        '''
        Refreshes a connection to server: disconnects and then connects again.
        '''
        
        self.disconnect()
        self.connect()

    def is_session_open(self):
        '''
        Checks if session with the server is open (i.e. at least one http
        request finished successfully)
        
        @rtype  : bool
        @returns: True if session is open, False otherwise.
        '''
        return self.session_id is not None

    def get_settings(self): # private
        """
        Loads application settings, which had been previously saved and
        returns host and port to connect to. Intended to be used in L{connect}
        method.
        
        @rtype : (string, string)
        @return: Returns host and port, where server is supposed to listen.        
        """
        self.settings = QSettings()

        network = TabNetwork()
        network.loadSettings(self.settings)

        host = network.addressHttpServer.text()
        port = network.portHttpServer.text()

        return (host, port)

    def request(self, url, params): # public
        '''
        Requests something from server.
        
        In case of success, writes response to .response variable and extracts
        sessionid from cookies. Returns True.
        
        If it cannot send request, it tries to reconnect.
        
        In case of unknown error, error code and description are written into
        .error_msg and False is returned
        
        Possible requests are listed below:
        - /manager/login/. Use this to authenticate on server. params are
            {'login': string, 'password': string}
        - /manager/get_rooms/. Get list of available rooms. params is empty
            dict.
        - /manager/static/. Get static information. params is empty dict.
            Static information is ???
        - /manager/get_client_info/. Get info about specific client. Client
        can be specified either by his UID, or by his RFID.
        In the former case params are {'rfid': RFID, 'mode': client},
        in the latter {'user_id':, 'mode': client}
        
        @type     url: string
        @param    url: URL to be requested.
        @type  params: dict
        @param params: Various parameters of the request. Vary depending on
            type of request.
        @rtype       : bool
        @return      : Return True if request succeeded, and False otherwise.
        @important   : All urls that can be requested (with meaning of these
            requests and description of parameters) should be added here.
        '''
        if self.session_id is not None and self.session_id not in self.headers:
            self.headers.update( { 'Cookie': 'sessionid=%s' % self.session_id } )

        # prepare parameters to pass to request() method of httplib
        params = urllib.urlencode(params)
        while True:
            # try to send a request
            try:
                self.conn.request('POST', url, params, self.headers)
                break
            # if that fails, try to reconnect
            except httplib.CannotSendRequest:
                self.reconnect()
            # if something unexpected happened, just print that out
            # and exit with error
            # !!! (Exception should be raised again)
            except Exception, e:
                self.error_msg = '[%s] %s' % (e.errno, e.strerror.decode('utf-8'))
                self.response = None
                return False

        self.response = self.conn.getresponse()

        # sessionid=d5b2996237b9044ba98c5622d6311c43;
        # expires=Tue, 09-Feb-2010 16:32:24 GMT;
        # Max-Age=1209600;
        # Path=/

        # Parse obtained cookies in order to obtain session_id
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
        '''
        Analyze response from server.
            - If succeeds, returns parsed JSON data as a dict;
            - On success in http status and error in JSON puts error message in
              .error_msg
            - On failure of http request recognizes requirement
              to authenticate (error 302), internal server error (error 500),
              in which case content of response is dumped into file ./dump.html
            - Unrecognized errors in http request are written to .error_msg
            
        In every case of failure 'default' value of http response is returned.
            
        @type  default: dict
        @param default: Value to return in case of failure.
        @rtype:         dict
        @return:        Dictionary representing json data in response.
        '''
        
        if not self.response: # request failed
            return None
        
        if self.response.status == 200: # http status
            data = self.response.read()
            
            # Decode JSON data from response
            # 2.5 and 2.6 versions compatibility included
            if hasattr(json, 'read'):
                response = json.read(data) # 2.5
            else:
                response = json.loads(data) # 2.6
            
            # if JSON response code is not equal to 200, something weird
            # happened
            # else, return decoded response
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
