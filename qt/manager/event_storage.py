# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time, operator
from datetime import datetime, date, time as dtime, timedelta

from os.path import dirname, join

from settings import _, DEBUG, userRoles
from http import Http

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Event(object):
    '''
    Class describing particular event.
    
    '''
    
    def __init__(self, monday, data_dict):
        '''
        '''
        
        self.monday = monday
        self.data = data_dict

        #self.dump(self.data)

        __ = lambda x: \
             datetime(*time.strptime(x, '%Y-%m-%d %H:%M:%S')[:6])

        self.begin_datetime = __( self.data['begin_datetime'] )
        self.end_datetime = __( self.data['begin_datetime'] )

        minutes = int( self.data['event']['duration'] * 60 )
        self.duration = timedelta(minutes=minutes)

    def dump(self, value):
        import pprint
        pprint.pprint(value)

    def __unicode__(self):
        return self.title

    def isTeam(self):
        return 'training' == self.data['type']

    def isRent(self):
        return 'rent' == self.data['type']

    @property
    def id(self):
        return int( self.data['id'] )

    @property
    def title(self):
        return self.data['event']['dance_styles']

    @property
    def coaches(self):
        # warning: self.data['event']['coaches'] contains of initial coaches list
        coach_names = ','.join([c['name'] for c in self.data['coaches']])
        return coach_names

    def set_coaches(self, coaches_list):
        self.data['coaches'] = coaches_list

    @property
    def tooltip(self):
        coach_names = ','.join([c['name'] for c in self.data['coaches']])
        event = self.data['event']
        return '%s\n%s\n%s' % (event['dance_styles'],
                           coach_names,
                           event['price_category']['title'])

    @property
    def fixed(self): #FIXME
        return int( self.data['status'] )

    def set_fixed(self, value):
        self.data['status'] = str(value)

class ModelStorage:
    '''
    Lowlevel structure, representing the timetable. Data is organized as
        follows:
    @important: add some general words here.
    
    @type SET: OP_TYPE
    @type GET: OP_TYPE
    @type DEL: OP_TYPE
    @cvar SET: Serves for specification of what action to perform with a
        given event, index. Same for GET and DEL.
        
    @type rc2e: dict
    @ivar rc2e: (row, col, room): event. Maps (row, column, room) triple into
        event, that takes place there.
    @type e2rc: dict
    @ivar e2rc: (event, room): [(row, col), (row, col), ...]. Maps
        (event, room) tuple into list of (row, columns), that are spanned by
        this event.
    
    @important: Setting/Getting/Deleting from/to rc2e and e2rc is done
        independently, so it is YOUR responsibility to ensure both lists are
        consistent with each other.
    
    @type  column: int
    @ivar column: Prevents access to columns with number less than column.
        Defaults to None.
    '''
    class OP_TYPE(int):
        pass
    SET = OP_TYPE(1)
    GET = OP_TYPE(2)
    DEL = OP_TYPE(3)

    def __init__(self):
        self.init()

    def init(self):
        self.column = None
        self.rc2e = {} # (row, col, room): event
        self.e2rc = {} # (event, room): [(row, col), (row, col), ...]

    def dump(self):
        '''
        Dump current timetable to standard output.
        '''
        import pprint
        pprint.pprint(self.rc2e)
        pprint.pprint(self.e2rc)

    def setFilter(self, column):
        '''
        Setter for self.column variable, that prevents access to some columns
            (see above).
        
        @type  column: int
        @param column: Number of first columns in timetable to hide.
        @return: None
        '''
        self.column = column

    def searchByID(self, id):
        '''
        Performs search of event in timetable by its ID.

        @type  id: int
        @param id: ID of the requested event.
        @rtype : Event
        @return: If found, returns corresponding L{Event} instance, otherwise
            None.
        '''
        for event, room in self.e2rc.keys():
            if event.id == id:
                return event
        return None

    def byRCR(self, op, key, value=None):
        '''
        Unified getter, setter, deleter method for individual cell in the
            model.
        
        @type  op: OP_TYPE.
        @param op: Action to be performed.
        @type  key: tuple(int, int, int)
        @param key: (row, column, room ID) triple, specifying particular cell
            in the timetable.
        @type  value: Event
        @param value: Optional. When op = ModelStorage.SET, event, specified by
        value is said to take place in the given cell.
        
        @raise Exception: If op does not match any of thought of operations,
            raise general type exception.
            
        @important: Add more specific exception types.
        '''
        if self.column is not None:
            row, column, room_id = key
            key = (row, column + self.column, room_id)
        if op == self.SET:
            return self.rc2e.update( { key: value } )
        elif op == self.GET:
            return self.rc2e.get(key, None)
        elif op == self.DEL:
            del(self.rc2e[key])
        else:
            raise _('ModelStorage: Unknown operation')

    def getByER(self, key):
        '''
        Get list of (rows, columns), that given (event, room) pair spans.
        
        @type  key: (Event, int)
        @param key: Tuple, containing particular event, and room number, where
            it takes place.  
        @rtype : list
        @return: Returns list of (row, column) tuples, that current event
            spans.
        '''
        cells = self.e2rc.get(key, None)
        if self.column is not None:
            result = []
            for row, column in cells:
                result.append((row, column - self.column))
            cells = result
        return cells

    def setByER(self, key, value):
        '''
        Set, which cells of the timetable current event spans.
        
        @type  key: (Event, int)
        @param key: Tuple, containing particular event, and room number, where
            it takes place.
        @type  value: list
        @param value: List of (row, column) tuples, that this particular event
            should span.
        @returns: None
        '''
        self.e2rc.update( { key: value } )

    def delByER(self, key):
        '''
        Delete current event from timetable.
        
        @type  key: (Event, int)
        @param key: Tuple, containing particular event, and room number, where
            it takes place.
        '''
        del(self.e2rc[key])

class EventStorage(QAbstractTableModel):
    '''
    Represents model of L{QtSchedule} widget.
    
    Attributes:
    
    @important: Duplicate variables: entries of params are with no reason
        (???) duplicated by individual variables.
        
    @type parent:  QWidget
    @ivar parent: View part of the widget
        (responsible for data-rendering).
    @type params:  dict
    @ivar params: Dictionary of parameters, which include:
        
        @type  work_hours: tuple(int, int)
        @param work_hours: The start and the end of working day. 
        @type  quant: datetime.timedelta
        @param quant: Minimal interval between the events in the timetable.
        @type   rooms: ???
        @param rooms: ???
        @type  mode: string
        @param mode: Either 'week' of 'day'. Specifies if the widget contains
            timetable for a week, or for a particular day.
    
    @type work_hours: tuple(int, int)
    @ivar work_hours: The start and the end of working day. 
    @type quant: datetime.timedelta
    @ivar quant: Minimal interval between the events in the timetable.
    @type  rooms: ???
    @ivar rooms: ???
    @type mode: string
    @ivar mode: Either 'week' of 'day'. Specifies if the widget contains
        timetable for a week, or for a particular day.
    @type week_days: [string, string, ...]
    @ivar week_days: List of names of days of the week. If mode == 'day', than
        internally 'week' is thought of as consisting from one day named 'Day'.
    @type multiplier: float
    @ivar multiplier: How many events (in principle) can occur in one hour?
    @type rows_count: int
    @ivar rows_count: Number of rows in a timetable for particular room.
    @type cols_count: int
    @ivar cols_count: Number of columns in a timetable (7 for weekly schedule
        and 1 for daily)
    @type weekRange: (datetime.date, datetime.date)
    @ivar weekRange: Tuple (Monday, Sunday) of the week shown.
    @type  storage: ModelStorage
    @param storage: Low-level representation of a timetable. Not for
        public use.
    '''
    def __init__(self, parent=None, params={}):
        '''
        @type  parent: QWidget
        @param parent: View of the model.
        @type  params: dict
        @param params: Dictionary of parameters, see L{params} attribute.
        '''
        # class originates from most basic table model.
        QAbstractTableModel.__init__(self, parent)

        self.parent = parent
        self.params = params

        self.work_hours = self.params.get('work_hours', None)
        self.quant = self.params.get('quant', None)
        self.rooms = self.params.get('rooms', None)
        self.mode = self.params.get('mode', 'week') # 'week' or 'day'

        if 'week' == self.mode:
            self.week_days = [ _('Monday'), _('Tuesday'),
                               _('Wednesday'), _('Thursday'),
                               _('Friday'), _('Saturday'),
                               _('Sunday') ]
        else:
            self.week_days = [ _('Day') ]

        begin_hour, end_hour = self.work_hours
        self.multiplier = timedelta(hours=1).seconds / self.quant.seconds
        self.rows_count = (end_hour - begin_hour) * self.multiplier
        self.cols_count = len(self.week_days)

        self.weekRange = self.date2range(datetime.now())

        # NOT USED YET: self.getMime = parent.getMime

        # Item storage
        self.storage = ModelStorage()
        self.storage_init()

    def storage_init(self):
        '''
        Wraps L{ModelStorage.init} method with signals.
        
        Needed for coordination with view part of the widget.
        '''
        self.emit(SIGNAL('layoutAboutToBeChanged()'))
        self.storage.init()
        self.emit(SIGNAL('layoutChanged()'))

    def update(self):
        '''
        Gets timetable from the server, only if schedule is showing weelky
        timetable.
        '''
        if 'week' == self.mode:
            self.load_data()

    def insert(self, room_id, event, emit_signal=False):
        '''
        This method registers new event. Wrapped in signals for coordination
        with 'view' part.
        '''
        self.emit(SIGNAL('layoutAboutToBeChanged()'))

        row, col = self.datetime2rowcol(event.begin_datetime)
        #self.beginInsertRows(QModelIndex(), row, row)
        cells = []
        for i in xrange(event.duration.seconds / self.quant.seconds):
            cells.append( (row + i, col) )
            self.storage.byRCR(ModelStorage.SET,
                               (row + i, col, room_id), event)
        self.storage.setByER( (event, room_id), cells )
        #self.endInsertRows()

        if emit_signal:
            self.emit(SIGNAL('layoutChanged()'))

    def remove(self, event, index, emit_signal=False):
        '''
        This method removes the event.
        '''
        room = event.data['room']['id']
        cell_list = self.get_cells_by_event(event, room)
        if cell_list:
            for row, col in cell_list:
                self.storage.byRCR(ModelStorage.DEL,
                                   (row, col, room))
            self.storage.delByER( (event, room) )
            if emit_signal and index:
                self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def change(self, event, index):
        '''
        Change event's info.
        '''
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def move(self, row, col, room, event):
        '''
        This method moves the event to new cell.
        '''
        self.remove(event, room)
        self.insert(row, col, room, event)

    def load_data(self):
        '''
        Requests information about current timetable from the server.
        
        Only performes request, if schedule is currently showing weekly, not
        daily, timetable.
        
        @important: Reimplement non-object-oriented handlement of status bar
            messages.
        '''
        if 'day' == self.mode:
            return False

        # THIS IS UGLY!!! NEED TO REIMPLEMENT
        self.parent.parent.statusBar().showMessage(_('Request information for the calendar.'))
        monday, sunday = self.weekRange

        http = self.params.get('http', None)
        if http and http.is_session_open():
            params = { 'monday': monday, 'filter': [] }
            http.request('/manager/get_week/', params) # FIXME: wrong place for HTTP Request!
            self.parent.parent.statusBar().showMessage(_('Parsing the response...'))
            response = http.parse(None)

            # result processing
            if response and 'events' in response:
                self.parent.parent.statusBar().showMessage(_('Filling the calendar...'))
                self.storage_init()
                # place the event in the model
                for event_info in response['events']:
                    qApp.processEvents() # keep GUI active
                    room_id = int( event_info['room']['id'] )
                    event_obj = Event(monday, event_info)
                    self.insert( room_id , event_obj )
                # draw events
                self.emit(SIGNAL('layoutChanged()'))
                self.parent.parent.statusBar().showMessage(_('Done'), 2000)
                # debugging
                #self.storage.dump()
                return True
            else:
                self.parent.parent.statusBar().showMessage(_('No reply'))
                return False

    def rowCount(self, parent): # protected
        if parent.isValid():
            return 0
        else:
            return self.rows_count

    def columnCount(self, parent): # protected
        if parent.isValid():
            return 0
        else:
            if 'week' == self.mode:
                return self.cols_count
            else:
                return 1

    def getShowMode(self):
        return self.mode

    def changeShowMode(self, column):
        if 'week' == self.mode:
            self.mode = 'day'
            self.storage.setFilter(column)
        else:
            self.mode = 'week'
            self.storage.setFilter(None)
        self.emit(SIGNAL('layoutChanged()'))

    def colByMode(self, column):
        if self.mode == 'week':
            return column
        else:
            return self.dayColumn

    def exchangeRoom(self, data_a, data_b):
        room_a = data_a[2]
        room_b = data_b[2]
        # events data
        event_a = self.storage.byRCR(ModelStorage.GET, data_a)
        event_b = self.storage.byRCR(ModelStorage.GET, data_b)
        # get cells list for each event
        items_a = self.storage.getByER( (event_a, room_a) )
        items_b = self.storage.getByER( (event_b, room_b) )
        # remove all records for each event
        self.remove(event_a, room_a)
        self.remove(event_b, room_b)
        # chech the exchange ability
        if self.may_insert(event_a, room_b) and \
                self.may_insert(event_b, room_a):
            # send the information to the server
            params = {'id_a': event_a.id,
                      'id_b': event_b.id}
            ajax = HttpAjax(self.parent, '/manager/exchange_room/',
                            params, self.parent.session_id)
            if ajax:
                response = ajax.parse_json()
                if response is not None:
                    # add events, exchanging rooms
                    self.insert(room_a, event_b)
                    self.insert(room_b, event_a)
                    self.emit(SIGNAL('layoutChanged()'))
                    return True
        # get back
        self.insert(room_a, event_a)
        self.insert(room_b, event_b)
        self.emit(SIGNAL('layoutChanged()'))
        return False

    def showCurrWeek(self):
        '''
        Display timetable for present week. Works only if schedule is in weekly
        mode.
        
        @important: Data is requested from a server on a call.
        
        @rtype : (datetime.date, datetime.date)
        @return: New L{weekRange<EventModel>} or None (if self.mode is unfit).
        '''
        if 'week' == self.mode:
            now = datetime.now()
            self.weekRange = self.date2range(now)
            self.load_data()
            return self.weekRange
        else:
            return None

    def showPrevWeek(self):
        '''
        Display timetable for previous week. Works only if schedule is in weekly
        mode.
        
        @important: Data is requested from a server on a call.
        
        @rtype : (datetime.date, datetime.date)
        @return: New L{weekRange<EventModel>} or None (if self.mode is unfit).
        '''
        if 'week' == self.mode:
            current_monday, current_sunday = self.weekRange
            prev_monday = current_monday - timedelta(days=7)
            prev_sunday = current_sunday - timedelta(days=7)
            self.weekRange = (prev_monday, prev_sunday)
            self.load_data()
            return self.weekRange
        else:
            return None

    def showNextWeek(self):
        '''
        Display timetable for the next week. Works only if schedule is in weekly
        mode.
        
        @important: Data is requested from a server on a call.
        
        @rtype : (datetime.date, datetime.date)
        @return: New L{weekRange<EventModel>} or None (if self.mode is unfit).
        '''
        if 'week' == self.mode:
            current_monday, current_sunday = self.weekRange
            next_monday = current_monday + timedelta(days=7)
            next_sunday = current_sunday + timedelta(days=7)
            self.weekRange = (next_monday, next_sunday)
            self.load_data()
            return self.weekRange
        else:
            return None

    def headerData(self, section, orientation, role):
        """ This method fills header cells. """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            mon, sun = self.weekRange
            if 'week' == self.mode:
                delta = section
            else:
                delta = self.storage.column
            daystr = (mon + timedelta(days=delta)).strftime('%d/%m')
            return QVariant('%s\n%s' % (self.week_days[delta], daystr))
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            begin_hour, end_hour = self.work_hours
            start = timedelta(hours=begin_hour)
            step = timedelta(seconds=(self.quant.seconds * section))
            return QVariant(str(start + step)[:-3])
        return QVariant()

    def data(self, index, role, room_id=0):
        """ This method returns the data from model. Parameter 'role' here means room. """
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole):
            return QVariant()
        row = index.row()
        col = index.column()
        event = self.get_event_by_cell(row, col, room_id)
        if event:
            if role == Qt.ToolTipRole:
                return QVariant( event.tooltip )
            if role == Qt.DisplayRole:
                cells = self.get_cells_by_event(event, room_id)
                if cells:
                    if cells[0] == (row, col):
                        event.show_type = 'head'
                    elif cells[-1] == (row, col):
                        event.show_type = 'tail'
                    else:
                        event.show_type = 'body'
                return QVariant(event)
        return QVariant()

    def getMonday(self):
        '''
        @rtype : datetime.date
        @return: Date of the Monday of the week shown.
        '''
        return self.weekRange[0]

    def getSunday(self):
        '''
        @rtype : datetime.date
        @return: Date of the Sunday of the week shown.
        '''
        return self.weekRange[1]

    def get_event_by_cell(self, row, col, room_id):
        """
        This methods returns the event that takes place in a given room and at
        timedate, specified by row and column of a timetable. 
        
        @type  row: int
        @param row: Row number of the cell.
        @type  col: int
        @param col: Column number of the cell.
        @type  room_id: int
        @param room_id: Number of the room, event takes place in.
        @rtype : Event
        @return: Event, that occurs (in particular) at the given position of
            the timetable.
        """
        return self.storage.byRCR(ModelStorage.GET, (row, col, room_id))

    def get_cells_by_event(self, event, room_id):
        """
        This method returns the cell list for given event.
        
        @type  event: Event
        @param event: Given event
        @type  room_id: int
        @param room_id: number of room, event takes place in.
        @rtype : [(int, int), ...]
        @return: List of tuples (row, column), that are spanned by given event.
        """
        return self.storage.getByER((event, room_id))

    def date2range(self, dt):
        '''
        This methods returns date of monday and sunday of the week, dt belongs
        to.
        
        @type  dt: datetime.datetime or datetime.date
        @param dt: A day, we want to know about
        @rtype : (date, date)
        @return: Returns corresponding Monday and Sunday as a tuple.
        '''
        
        if type(dt) is datetime:
            dt = dt.date()
        monday = dt - timedelta(days=dt.weekday())
        sunday = monday + timedelta(days=6)
        return (monday, sunday)

    def date2timestamp(self, d):
        '''
        Returns a timestamp of a given datetime.
        
        @type  d: datetime.datetime
        @param d: Any datetime
        @rtype : float
        @return: A timestamp
        '''
        return int(time.mktime(d.timetuple()))

    def datetime2rowcol(self, dt):
        '''
        Returns, to which cell of a timetable current datetime dt fits.
        
        @type  dt: datetime.datetime
        @param dt: Just any datetime structure.
        @rtype : (int, int)
        @return: A tuple (row, column), specifying a cell in timetable.
        '''
        row = (dt.hour - self.work_hours[0]) * self.multiplier
        if dt.minute >= 30:
            row += 1
        col = dt.weekday()
        #print '%s %s %s' % (dt, row, col)
        return (row, col)

    def may_insert(self, event, room_id):
        """ This method checks the ability of placing the event on schedule. """
        row, col = self.datetime2rowcol(event.begin)
        for i in xrange(event.duration.seconds / self.quant.seconds):
            if self.storage.byRCR(
                ModelStorage.GET,
                (row + i, col, room_id)
                ) is not None:
                return False
        return True

#     def prepare_event_cells(self, event, room_id, row, col):
#         cells = []
#         for i in xrange(event.duration.seconds / self.quant.seconds):
#             cells.append( (row + i, col, room_id) )
#         return cells

#     def get_free_rooms(self, event, row, col):
#         """ Метод для проверки возможности размещения события по указанным
#         координатам. Возвращает список залов, которые предоставляют такую
#         возможность.

#         Для каждого зала из списка проверить наличие свободных
#         интервалов времени.
#         """
#         result = []
#         for room_name, room_color, room_id in self.rooms:
#             free = []
#             for i in xrange(event.duration.seconds / self.quant.seconds):
#                 free.append( self.rc2e.get( (row + i, col, room_id), None ) is None )
#             print free

#             if reduce( lambda x,y: x and y, free ):
#                 result.append(room_id)
#         return result

    # DnD support - the begin

    def supportedDropActions(self):
        """
        This method defines DnD actions supported by this model.
        
        These are 'copy' and 'move'.
        """
        
        if DEBUG:
            print 'EventStorage::supportedDropActions'
        return (Qt.CopyAction | Qt.MoveAction)

    def flags(self, index):
        """ This method defines the list of items that may in DnD operations. """
        #if DEBUG:
        #    print 'EventStorage::flags', index.row(), index.column()
        if index.isValid():
            res = (Qt.ItemIsEnabled | Qt.ItemIsSelectable
                   | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        else:
            res = (Qt.ItemIsEnabled | Qt.ItemIsDropEnabled)
        return res

    def mimeTypes(self):
        """ This method declares supported MIME types. """
        types = QStringList()
        types << self.getMime('event') << self.getMime('team')
        return types

    def mimeData(self, indexes):
        """ This method converts objects into supported MIME format. """
        mimeData = QMimeData()
        encodedData = QByteArray()

        stream = QDataStream(encodedData, QIODevice.WriteOnly)

        events = []

        if DEBUG:
            print indexes

            for index in indexes:
                if index.isValid():
                    print dir(index)
                    print self.data(index, 100)

        mimeData.setData(self.getMime('event'), encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        if action == Qt.IgnoreAction:
            return True

        event_mime = self.getMime('event')
        team_mime = self.getMime('team')

        if not data.hasFormat(event_mime) and \
                not data.hasFormat(team_mime):
            return False
        if column > 0:
            return False

        itemData = data.data(event_mime)
        dataStream = QDataStream(itemData, QIODevice.ReadOnly)

        id = QString()
        stream >> id

        return True

    def setData(self, index, value, role):
        """ Parameter 'role' means room. """
        return True

    def setHeaderData(self, section, orientation, value, role):
        return True

#     def removeRows(self, row, count, parent):
#         print 'EventStorage::removeRows'
#         if parent.isValid():
#             return False

#         self.beginRemoveRows(parent, row, row)
#         # remove here
#         self.endRemoveRows()
#         return True

#     def insertRows(self, row, count, parent):
#         print 'EventStorage::insertRows'

    # DnD support - the end

