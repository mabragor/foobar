#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, timedelta
from os.path import dirname, join

from settings import _, DEBUG
from http import Http
from event_storage import Event
from qtschedule import QtSchedule

from team_tree import TreeModel

from dialogs.rfid_wait import WaitingRFID
from dialogs.searching import Searching
from dialogs.user_info import ClientInfo, DlgRenterInfo
from dlg_settings import DlgSettings
from dlg_login import DlgLogin
from dlg_event_assign import DlgEventAssign
from dlg_event_info import EventInfo
from dlg_copy_week import DlgCopyWeek
from dlg_accounting import DlgAccounting

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MainWindow(QMainWindow):
    '''
    Describes main window of a client application.
    '''
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.mimes = {'team': 'application/x-team-item',
                      'event':  'application/x-calendar-event',
                      }
        self.rooms = []
        self.tree = []
        self.rfid_id = None

        self.http = Http(self)

        self.work_hours = (8, 24)
        self.schedule_quant = timedelta(minutes=30)

        self.menus = []
        self.create_menus()
        self.setup_views()

        settings = QSettings()
        settings.beginGroup('network')
        host = settings.value('addressHttpServer', QVariant('WrongHost'))
        settings.endGroup()

        if 'WrongHost' == host.toString():
            self.setupApp()

        self.baseTitle = _('Manager\'s interface')
        self.logoutTitle()
        self.statusBar().showMessage(_('Ready'), 2000)
        self.resize(640, 480)

    def loggedTitle(self, name):
        '''
        Appends name of a manager to basic title of main window. Indended to be
        called after successful L{log in<???>}.
        
        @type  name: string
        @param name: Name of a manager, that have logged in.
        '''
        self.setWindowTitle('%s : %s' % (self.baseTitle, name))

    def logoutTitle(self):
        '''
        Appends 'Log in to start session' to basic title of main window.
        Indended to be used on L{logout<>} and when application
        L{starts<__init__>}. 
        '''
        
        self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))

    def get_dynamic(self):
        '''
        Updates L{labels<create_views>} bpMonday and bpSunday, that show date
        of beginning and end of the week, that is currently displayed by
        L{QtSchedule} widget.
        '''
        
        self.bpMonday.setText(self.schedule.model().getMonday().strftime('%d/%m/%Y'))
        self.bpSunday.setText(self.schedule.model().getSunday().strftime('%d/%m/%Y'))

    def get_static(self):
        """
        Gets static information from server.
        
        First, all present rooms are L{retrieved<Http.request>}. They are
        returned as a dict in the following format::
            {'rows': [{'color': 'FFAAAA', 'text': 'red', 'id': 1},
                  {'color': 'AAFFAA', 'text': 'green', 'id': 2},
            ...]}
        
        Then, other static info is retrieved???
        """
        # get rooms
        if not self.http.request('/manager/get_rooms/', {}):
            QMessageBox.critical(self, _('Room info'), _('Unable to fetch: %s') % self.http.error_msg)
            return
        default_response = {'rows': []}
        response = self.http.parse(default_response)
        
        self.rooms = tuple( [ (a['title'], a['color'], a['id']) for a in response['rows'] ] )
        self.schedule.update_static( {'rooms': self.rooms} )

        # static info
        if not self.http.request('/manager/static/', {}):
            QMessageBox.critical(self, _('Static info'), _('Unable to fetch: %s') % self.http.error_msg)
            return
        response = self.http.parse()
        self.static = response
        print 'Static is', self.static.keys()
        #import pprint; pprint.pprint(self.static)

        #self.tree = TreeModel(self.static.get('styles', None))

    def update_interface(self):
        """ This method updates application's interface using static
        information obtained in previous method. """
        # rooms
        if self.rooms and len(self.rooms) > 0:
            for title, color, id in self.rooms:
                buttonFilter = QPushButton(title)
                buttonFilter.setCheckable(True)
                buttonFilter.setDisabled(True) # BUG #28
                self.panelRooms.addWidget(buttonFilter)
                self.connect(buttonFilter, SIGNAL('clicked()'),
                             self.prepare_filter(id, title))

    def prepare_filter(self, id, title):
        def handler():
            self.statusBar().showMessage(_('Filter: Room "%s" is changed its state') % title)
        return handler

    def setup_views(self):
        '''
        This method sets up layout of main window, except for dropdown menus.
        
        At the center of the window there is a custon L{QtSchedule} widget,
        which shows timetable of some week or of particular day.
        
        Under it there are widgets for navigation: two labels bpMonday and
        bpSunday display information on what date range is displayed in
        schedule widget, and buttons buttonPrev, buttonNext and buttonToday
        are used to tell schedule to show previous week, next week and current
        week respectively.
        '''
        self.panelRooms = QHBoxLayout()

        schedule_params = {
            'http': self.http,
            'work_hours': self.work_hours,
            'quant': self.schedule_quant,
            'rooms': self.rooms,
            }
        self.schedule = QtSchedule(self, schedule_params)

        self.bpMonday = QLabel('--/--/----')
        self.bpSunday = QLabel('--/--/----')
        self.buttonPrev = QPushButton(_('<<'))
        self.buttonNext = QPushButton(_('>>'))
        self.buttonToday = QPushButton(_('Today'))
        self.buttonPrev.setDisabled(True)
        self.buttonNext.setDisabled(True)
        self.buttonToday.setDisabled(True)

        # callback helper function
        def prev_week():
            week_range = self.schedule.model().showPrevWeek()
            self.showWeekRange(week_range)
        def next_week():
            week_range = self.schedule.model().showNextWeek()
            self.showWeekRange(week_range)
        def today():
            week_range = self.schedule.model().showCurrWeek()
            self.showWeekRange(week_range)

        self.connect(self.buttonPrev, SIGNAL('clicked()'), prev_week)
        self.connect(self.buttonNext, SIGNAL('clicked()'), next_week)
        self.connect(self.buttonToday, SIGNAL('clicked()'), today)

        bottomPanel = QHBoxLayout()
        bottomPanel.addWidget(QLabel(_('Week:')))
        bottomPanel.addWidget(self.bpMonday)
        bottomPanel.addWidget(QLabel('-'))
        bottomPanel.addWidget(self.bpSunday)
        bottomPanel.addStretch(1)
        bottomPanel.addWidget(self.buttonPrev)
        bottomPanel.addWidget(self.buttonToday)
        bottomPanel.addWidget(self.buttonNext)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.panelRooms)
        mainLayout.addWidget(self.schedule)
        mainLayout.addLayout(bottomPanel)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

    def showWeekRange(self, week_range):
        if self.schedule.model().getShowMode() == 'week':
            monday, sunday = week_range
            self.bpMonday.setText(monday.strftime('%d/%m/%Y'))
            self.bpSunday.setText(sunday.strftime('%d/%m/%Y'))

    def getMime(self, name):
        return self.mimes.get(name, None)

    def create_menus(self):
        """
        This method generates the application dropdown menu.
        
        Menu items are specified in 'data' variable inside the method.
        Format is as follows:
        - data is list of tuples of form (menu_title, list_of_submenus), where
        menu_name is the name of a given menu (e.g. 'File') and
        list_of_submenus contains menu items, that drop down, when you click
        on menu_name.
        - submenu items are tuples (title, shortcut, handler function, comment)
        
        Current menu structure is as follows:
        - File.
            - L{Log in<login>}.
            - L{Log out<logout>}.
            - L{Application settings<setupApp>}.
            - Exit.
        - Client. 
            - L{New<client_new>}.
            - L{Search by RFID<client_search_rfid>}.
            - L{Search by name<client_search_name>}.
        - Renter.
            - L{New<renterNew>}.
            - L{Search by name<renterSearchName>}.
        - Calendar.
            - L{Fill week<fillWeek>}.
            
        @important: Style of naming of functions is mixed!!!
        """
        data = [
            (_('File'), [
                (_('Log in'), 'Ctrl+I',
                 'login', _('Start user session.')),
                (_('Log out'), '',
                 'logout', _('End user session.')),
                None,
                (_('Application settings'), 'Ctrl+G',
                 'setupApp', _('Manage the application settings.')),
                None,
                (_('Exit'), '',
                 'close', _('Close the application.')),
                ]
             ),
            (_('Client'), [
                (_('New'), 'Ctrl+N',
                 'client_new', _('Register new client.')),
                (_('Search by RFID'), 'Ctrl+D',
		     'client_search_rfid', _('Search a client with its RFID card.')),
                (_('Search by name'), 'Ctrl+F',
                 'client_search_name', _('Search a client with its name.')),
                ]
             ),
            (_('Renter'), [
                (_('New'), '',
                 'renterNew', _('Register new renter.')),
                (_('Search by name'), '',
                 'renterSearchName', _('Search a renter with its name.')),
                ]
             ),
            # 	    (_('Event'), [
            # 		    (_('Training'), 'Ctrl+T',
            # 		     'eventTraining', _('Assign a training event.')),
            # 		    (_('Rent'), 'Ctrl+R',
            # 		     'eventRent', _('Assign a rent event.')),
            #                     ]
            #              ),
            (_('Calendar'), [
                (_('Fill week'), 'Ctrl+L',
                 'fillWeek', _('Fill current week.')),
                # 		    (_('Copy week'), 'Ctrl+W',
                # 		     'copyWeek', _('Copy current week into other.')),
                ]
             ),
            # 	    (_('Accounting'), [
            # 		    (_('Add resources'), '',
            # 		     'addResources', _('Add new set of resources into accounting.')),
            #                     ]
            #              ),
            ]

        for topic, info in data:
            menu = self.menuBar().addMenu(topic)
            # Disable the following menu actions, until user will be authorized.
            if topic != _('File'):
                menu.setDisabled(True)
            for item in info:
                if item is None:
                    menu.addSeparator()
                    continue
                title, short, name, desc = item
                setattr(self, 'act_%s' % name, QAction(title, self))
                action = getattr(self, 'act_%s' % name)
                action.setShortcut(short)
                action.setStatusTip(desc)
                self.connect(action, SIGNAL('triggered()'), getattr(self, name))
                menu.addAction(action)
                self.menus.append(menu)

    def interface_disable(self, state): # True = disabled, False = enabled
        '''
        This method is to be invoked on L{log out<logout>} or when the
        application L{starts<__init__>}.
        
        It disables schedule navigation buttons and L{all dropdown menus except
        File<create_menus>}.
        '''
        # Enable menu's action
        for menu in self.menus:
            if menu.title() != _('File'):
                menu.setDisabled(state)
        # Enable the navigation buttons
        self.buttonPrev.setDisabled(state)
        self.buttonNext.setDisabled(state)
        self.buttonToday.setDisabled(state)

    def refresh_data(self):
        """
        This method gets current timetable from the server using
        L{update<QtSchedule.update>} method of L{QtSchedule} widget.
        
        It is called periodically using timer. Interaction with server only
        occurs if manager is logged in.
        """

        # Do nothing until user authoruized
        if not self.http.is_session_open():
            return
        # Just refresh the calendar's model
        self.schedule.model().update

    # Menu handlers: The begin

    def login(self):
        '''
        Shows log in dialog, where manager is asked to provide login/password
        pair.
        
        If 'Ok' button is clicked, authentication L{request<Http.request>} is
        made to the server, which is then L{parsed<Http.parse>}.
        
        On success:
        - information about schedule is retrieved from the server and
        and L{QtSchedule} widget is L{updated<update_interface>}.
        - controls are L{activated<interface_disable>}.
        - window title is L{updated<loggedTitle>}
        - schedule information is being L{refreshed<refresh_data>} from now on.
        
        In case of failure to authenticate a message is displayed.
        '''
         
        def callback(credentials):
            self.credentials = credentials

        self.dialog = DlgLogin(self)
        self.dialog.setCallback(callback)
        self.dialog.setModal(True)
        dlgStatus = self.dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            if not self.http.request('/manager/login/', self.credentials):
                QMessageBox.critical(self, _('Login'), _('Unable to login: %s') % self.http.error_msg)
                return

            default_response = None
            response = self.http.parse(default_response)
            if response and 'user_info' in response:
                self.loggedTitle(response['user_info'])

                # update application's interface
                self.get_static()
                self.get_dynamic()
                self.update_interface()

                self.schedule.model().showCurrWeek()

                # run refresh timer
                self.refreshTimer = QTimer(self)
                from settings import SCHEDULE_REFRESH_TIMEOUT
                self.refreshTimer.setInterval(SCHEDULE_REFRESH_TIMEOUT)
                self.connect(self.refreshTimer, SIGNAL('timeout()'), self.refresh_data)
                self.refreshTimer.start()

                self.interface_disable(False)
            else:
                QMessageBox.warning(self, _('Login failed'),
                                    _('It seems you\'ve entered wrong login/password.'))

    def logout(self):
        '''
        Performs sequence of clean up actions when manager logs out:
        - L{disables controls<interface_disable>};
        - Deletes information about schedule and rooms, that are present.
        '''
        self.interface_disable(True)
        self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))
        self.schedule.model().storage_init()

        # clear rooms layout
        layout = self.panelRooms
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

    def setupApp(self):
        '''
        Displays dialog with settings for client application.
        
        After that date range, that is being displayed is refreshed and
        L{reconnect<Http.reconnect>} to server is performed (just in case network settings)
        had been altered.
        '''
        self.dialog = DlgSettings(self)
        self.dialog.setModal(True)
        self.dialog.exec_()
        self.get_dynamic()
        self.http.reconnect()

    def client_new(self):
        '''
        Opens empty client information L{dialog<ClientInfo>} for adding
        new client to the database.
        
        Class for L{accessing server<Http>} and static information (???) are
        passed as parameters.
        '''
        params = {
            'http': self.http,
            'static': self.static,
            }
        self.dialog = ClientInfo(self, params)
        self.dialog.setModal(True)
        self.dialog.exec_()

    def client_search_rfid(self):
        '''
        Search client in the database
        by RFID (Radio Frequency IDentificator).
        
        After RFID was successfully read from card, server is
        L{requested<Http.request>} client info.
        
        If user is found in database, L{dialog<ClientInfo>}
        with information about client is displayed.
        
        Otherwise, messageboxes with warnings are displayed.
        '''
        
        if not self.http or not self.http.is_session_open():
            return # login first

        def callback(rfid):
            self.rfid_id = rfid

        params = {
            'http': self.http,
            'static': self.static,
            'mode': 'client',
            'callback': callback,
            }
        dialog = WaitingRFID(self, params)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

        if QDialog.Accepted == dlgStatus and self.rfid_id is not None:
            params = {'rfid_code': self.rfid_id, 'mode': 'client'}
            if not self.http.request('/manager/get_client_info/', params):
                QMessageBox.critical(self, _('Client info'), _('Unable to fetch: %s') % self.http.error_msg)
                return
            default_response = None
            response = self.http.parse(default_response)

            if not response or response['info'] is None:
                QMessageBox.warning(self, _('Warning'),
                                    _('This RFID belongs to nobody.'))
            else:
                user_info = response['info']
                params = {
                    'http': self.http,
                    'static': self.static,
                    }
                self.dialog = ClientInfo(self, params)
                self.dialog.setModal(True)

                self.dialog.initData(user_info)
                self.dialog.exec_()
                self.rfid_id = None

    def client_search_name(self):
        '''
        Search client in the database by name.
        
        First it launches client search L{dialog<Searching>}, which
        tries to fetch unique user_id from the server based on information
        provided.
        
        If that succeeds, user_id-based search then Works analogously to
        L{RFID-based<client_search_rfid>} search.
        '''
        if not self.http or not self.http.is_session_open():
            return # login first

        def callback(user_id):
            self.user_id = user_id

        params = {
            'http': self.http,
            'static': self.static,
            'mode': 'client',
            'apply_title': _('Show'),
            }
        self.dialog = Searching(self, params)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        dlgStatus = self.dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            if not self.http.request('/manager/get_client_info/',
                                     {'user_id': self.user_id,
                                      'mode': 'client'}):
                QMessageBox.critical(self, _('Client info'), _('Unable to fetch: %s') % self.http.error_msg)
                return
            default_response = None
            response = self.http.parse(default_response)
            if not response or response['info'] is None:
                QMessageBox.warning(self, _('Warning'),
                                    _('This RFID belongs to nobody.'))
            else:
                params = {
                    'http': self.http,
                    'static': self.static,
                    }
                self.dialog = ClientInfo(self, params)
                self.dialog.setModal(True)
                self.dialog.initData(response['info'])
                self.dialog.exec_()

    def renterNew(self):
        '''
        Adding new renter.
        '''
        self.dialog = DlgRenterInfo(self)
        self.dialog.setModal(True)
        self.dialog.exec_()

    def renterSearchName(self):
        '''
        Search renter by his name.
        
        @important: by some strange reason, HttpAjax class is used instead of
        Http to fetch information from the server.
        '''
        def callback(id):
            self.user_id = id

        params = {
            'http': self.http,
            'static': self.static,
            'mode': 'client',
            }
        self.dialog = Searching(self, params)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        dlgStatus = self.dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            ajax = HttpAjax(self, '/manager/get_renter_info/',
                            {'user_id': self.user_id,
                             'mode': 'renter'}, self.session_id)
            response = ajax.parse_json()
            self.dialog = DlgRenterInfo(self)
            self.dialog.setModal(True)
            self.dialog.initData(response['info'])
            self.dialog.exec_()

    def eventTraining(self):
        def callback(e_date, e_time, room_tuple, team):
            room, ok = room_tuple
            title, team_id, count, price, coach, duration = team
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(minutes=int(duration * 60))

            ajax = HttpAjax(self, '/manager/cal_event_add/',
                            {'event_id': team_id,
                             'room_id': room,
                             'begin': begin,
                             'ev_type': 0}, self.session_id)
            response = ajax.parse_json()
            id = int(response['saved_id'])
            event_info = {'id': id,
                          'title': title, 'price': price,
                          'count': count, 'coach': coach,
                          'duration': duration,
                          'groups': _('Waiting for update.')}
            eventObj = Event({}) # FIXME
            self.schedule.insertEvent(room, eventObj)

        self.dialog = DlgEventAssign('training', self)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setModel(self.tree)
        self.dialog.setRooms(self.rooms)
        self.dialog.exec_()

    def eventRent(self):
        def callback(e_date, e_time, e_duration, room_tuple, rent):
            room, ok = room_tuple
            rent_id = rent['id']
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(hours=e_duration.hour,
                                 minutes=e_duration.minute)
            params = {
                'event_id': rent_id,
                'room_id': room,
                'begin': begin,
                'ev_type': 1,
                'duration': float(duration.seconds) / 3600
                }
            ajax = HttpAjax(self, '/manager/cal_event_add/', params, self.session_id)
            response = ajax.parse_json()
            id = int(response['saved_id'])
            eventObj = Event({}) # FIXME
            self.schedule.insertEvent(room, eventObj)

        self.dialog = DlgEventAssign('rent', self)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setRooms(self.rooms)
        self.dialog.exec_()

    def fillWeek(self):
        def callback(selected_date):
            model = self.schedule.model()
            from_range = model.weekRange
            to_range = model.date2range(selected_date)

            if not self.http.request('/manager/fill_week/', {'to_date': to_range[0]}):
                QMessageBox.critical(self, _('Fill week'), _('Unable to fill: %s') % self.http.error_msg)
                return
            default_response = None
            response = self.http.parse(default_response)
            if response and 'saved_id' in response:
                # inform user
                info = response['saved_id']
                msg = _('The week has been filled sucessfully. Copied: %(copied)i. Passed: %(passed)i.')
                self.statusBar().showMessage(msg % info, 3000)
                # FIXME: pause here, but not just sleep, use timer
                # update view
                self.schedule.model().update()

        self.dialog = DlgCopyWeek(self)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.exec_()

    def copyWeek(self):
        def callback(selected_date):
            model = self.scheduleModel
            from_range = model.weekRange
            to_range = model.date2range(selected_date)
            ajax = HttpAjax(self, '/manager/copy_week/',
                            {'from_date': from_range[0],
                             'to_date': to_range[0]}, self.session_id)
            response = ajax.parse_json()
            self.statusBar().showMessage(_('The week has been copied sucessfully.'))

        self.dialog = DlgCopyWeek(self)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.exec_()

    def addResources(self):
        def callback(count, price):
#             ajax = HttpAjax(self, '/manager/add_resource/',
#                             {'from_date': from_range[0],
#                              'to_date': to_range[0]}, self.session_id)
            response = ajax.parse_json()
            self.statusBar().showMessage(_('The week has been copied sucessfully.'))

        self.dialog = DlgAccounting(self)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.exec_()

    # Menu handlers: The end

#def getUserInfo(self, rfid):
# 	""" This method get user's information by its card's identifier. """
# 	ajax = HttpAjax(self, '/manager/get_client_info/',
# 			{'rfid_code': rfid, mode='client'})
# 	json_like = ajax.parse_json()
# 	print 'USER INFO:', json_like
# 	return json_like

    def showEventProperties(self, calendar_event, index): #, room_id):
        self.dialog = EventInfo(self, {'http': self.http})
        self.dialog.setModal(True)
        self.dialog.initData(calendar_event, index)
        self.dialog.exec_()

    # Drag'n'Drop section begins
    def mousePressEvent(self, event):
        if DEBUG:
            print 'press event', event.button()

    def mouseMoveEvent(self, event):
        if DEBUG:
            print 'move event', event.pos()
    # Drag'n'Drop section ends


if __name__=="__main__":

    def readStyleSheet(fileName) :
        css = QString()
        file = QFile(join(dirname(__file__), fileName))
        if file.open(QIODevice.ReadOnly) :
                css = QString(file.readAll())
                file.close()
        return css

    # application global settings
    QCoreApplication.setOrganizationName('Home, Sweet Home')
    QCoreApplication.setOrganizationDomain('snegiri.dontexist.org')
    QCoreApplication.setApplicationName('foobar')
    QCoreApplication.setApplicationVersion('0.1')

    app = QApplication(sys.argv)
    app.setStyleSheet(readStyleSheet('manager.css'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
