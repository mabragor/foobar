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

    """ Класс события. """

    def __init__(self, monday, data_dict):
        self.monday = monday
        self.data = data_dict

        #self.dump(self.data)

        __ = lambda x: \
             datetime(*time.strptime(x, '%Y-%m-%d %H:%M:%S')[:6])

        self.begin_datetime = __( self.data['begin_datetime'] )
        self.end_datetime = __( self.data['begin_datetime'] )

        minutes = int( self.data['event']['duration'] * 60 )
        self.duration = timedelta(minutes=minutes)

        demo = {'id': 10,
                'room': {'color': 'FFAAAA', 'id': 1, 'title': 'red'},
                'begin_datetime': '2010-04-28 17:00:00',
                'end_datetime': '2010-04-28 18:00:00',
                'event': {'coach': {'birth_date': '2010-04-30',
                                    'desc': u'\u0431\u0443\u0445\u0430\u0435\u0442',
                                    'email': 'ivan@jet.ru',
                                    'first_name': u'\u0418\u0432\u0430\u043d',
                                    'id': 2,
                                    'last_name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439',
                                    'name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439 \u0418\u0432\u0430\u043d',
                                    'phone': '1234567890'},
                          'duration': 1.0,
                          'groups': u'\u0421\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0435 \u0442\u0430\u043d\u0446\u044b',
                          'id': 1,
                          'price_category': '0',
                          'title': u'\u0411\u0440\u0435\u0439\u043a-\u0434\u0430\u043d\u0441 \u0438 free style'},
                'event_fixed': '0',
                'type': 'training'}

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
        return self.data['event']['title']

    @property
    def coach(self):
        return self.data['event']['coach']['name']

    @property
    def fixed(self): #FIXME
        return int( self.data['status'] )

class ModelStorage:

    SET = 1; GET = 2; DEL = 3

    def __init__(self):
        self.init()

    def init(self):
        self.column = None
        self.rc2e = {} # (row, col, room): event
        self.e2rc = {} # (event, room): [(row, col), (row, col), ...]

    def dump(self):
        import pprint
        pprint.pprint(self.rc2e)
        pprint.pprint(self.e2rc)

    def setFilter(self, column):
        self.column = column

    def searchByID(self, id):
        for event, room in self.e2rc.keys():
            if event.id == id:
                return event
        return None

    def byRCR(self, op, key, value=None):
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
        cells = self.e2rc.get(key, None)
        if self.column is not None:
            result = []
            for row, column in cells:
                result.append((row, column - self.column))
            cells = result
        return cells

    def setByER(self, key, value):
        self.e2rc.update( { key: value } )

    def delByER(self, key):
        del(self.e2rc[key])

class EventStorage(QAbstractTableModel):

    def __init__(self, parent=None, params={}):
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

        # Хранилище элементов
        self.storage = ModelStorage()
        self.storage.init() # очистка

    def update(self):
        if 'week' == self.mode:
            self.load_data()

    def insert(self, room_id, event, emit_signal=False):
        """ Метод регистрации нового события. """
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

    def remove(self, event_id, room, emit_signal=False):
        """ Метод удаления информации о событии. """
        event = self.storage.searchByID(event_id)
        if event is None:
            return
        cell_list = self.get_cells_by_event(event, room)
        if cell_list:
            for row, col in cell_list:
                self.storage.byRCR(ModelStorage.DEL,
                                   (row, col, room))
            self.storage.delByER( (event, room) )
            if emit_signal:
                self.emit(SIGNAL('layoutChanged()'))

    def move(self, row, col, room, event):
        """ Метод перемещения события по координатной сетке. """
        self.remove(event, room)
        self.insert(row, col, room, event)

    def load_data(self):
        if 'day' == self.mode:
            return False

        self.parent.parent.statusBar().showMessage(_('Request information for the calendar.'))
        monday, sunday = self.weekRange

        http = self.params.get('http', None)
        if http and http.is_session_open():
            params = { 'monday': monday, 'filter': [] }
            http.request('/manager/get_week/', params)
            self.parent.parent.statusBar().showMessage(_('Parsing the response...'))
            response = http.parse(None)

            # обработка результатов
            if response and 'events' in response:
                self.parent.parent.statusBar().showMessage(_('Filling the calendar...'))
                self.storage.init()
                # размещаем событие в модели
                for event_info in response['events']:
                    qApp.processEvents() # keep GUI active
                    room_id = int( event_info['room']['id'] )
                    event_obj = Event(monday, event_info)
                    self.insert( room_id , event_obj )
                # отображаем события
                self.emit(SIGNAL('layoutChanged()'))
                self.parent.parent.statusBar().showMessage(_('Done'), 2000)
                # отладочный вывод
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
            selfmode = 'day'
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
        # paramsсодержит идентификаторы событий
        room_a = data_a[2]
        room_b = data_b[2]
        # получить данные о событиях
        event_a = self.storage.byRCR(ModelStorage.GET, data_a)
        event_b = self.storage.byRCR(ModelStorage.GET, data_b)
        # получить списки ячеек для каждого события
        items_a = self.storage.getByER( (event_a, room_a) )
        items_b = self.storage.getByER( (event_b, room_b) )
        # удалить все записи о каждом событии
        self.remove(event_a, room_a)
        self.remove(event_b, room_b)
        # проверить возможность обмена
        if self.may_insert(event_a, room_b) and \
                self.may_insert(event_b, room_a):
            # отправить инфо на сервер
            params = {'id_a': event_a.id,
                      'id_b': event_b.id}
            ajax = HttpAjax(self.parent, '/manager/exchange_room/',
                            params, self.parent.session_id)
            if ajax:
                response = ajax.parse_json()
                if response is not None:
                    # добавить события, обменяв залы
                    self.insert(room_a, event_b)
                    self.insert(room_b, event_a)
                    self.emit(SIGNAL('layoutChanged()'))
                    return True
        # вертать взад
        self.insert(room_a, event_a)
        self.insert(room_b, event_b)
        self.emit(SIGNAL('layoutChanged()'))
        return False

    def showCurrWeek(self):
        if 'week' == self.mode:
            now = datetime.now()
            self.weekRange = self.date2range(now)
            self.load_data()
            return self.weekRange
        else:
            return None

    def showPrevWeek(self):
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
        """ Метод для определения вертикальных и горизонтальных меток для
        рядов и колонок таблицы. """
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
        """ Перегруженный метод базового класса. Под ролью понимаем зал. """
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole):
            return QVariant()
        row = index.row()
        col = index.column()
        event = self.get_event_by_cell(row, col, room_id)
        if event:
            if role == Qt.ToolTipRole:
                tooltip = '%s\n%s' % (event.title, event.coach)
                return QVariant(tooltip)
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
        return self.weekRange[0]

    def getSunday(self):
        return self.weekRange[1]

    def get_event_by_cell(self, row, col, room_id):
        """ Получение события по указанным координатам. """
        return self.storage.byRCR(ModelStorage.GET, (row, col, room_id))

    def get_cells_by_event(self, event, room_id):
        """ Получение всех ячеек события. """
        return self.storage.getByER( (event, room_id) )

    def date2range(self, dt):
        """ Возвращаем диапазон недели для переданной даты. """
        if type(dt) is datetime:
            dt = dt.date()
        monday = dt - timedelta(days=dt.weekday())
        sunday = monday + timedelta(days=6)
        return (monday, sunday)

    def date2timestamp(self, d):
        return int(time.mktime(d.timetuple()))

    def datetime2rowcol(self, dt):
        row = (dt.hour - self.work_hours[0]) * self.multiplier
        if dt.minute >= 30:
            row += 1
        col = dt.weekday()
        #print '%s %s %s' % (dt, row, col)
        return (row, col)

    def may_insert(self, event, room_id):
        """ Метод для проверки позможности размещения события по указанным
        координатам. Возвращает True/False. """
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

    # Поддержка Drag'n'Drop - начало секции

    def supportedDropActions(self):
        """ Метод для определения списка DnD действий, поддерживаемых
        моделью. """
        if DEBUG:
            print 'EventStorage::supportedDropActions'
        return (Qt.CopyAction | Qt.MoveAction)

    def flags(self, index):
        """ Метод для определения списка элементов, которые могут участвовать
        в DnD операциях. """
        #if DEBUG:
        #    print 'EventStorage::flags', index.row(), index.column()
        if index.isValid():
            res = (Qt.ItemIsEnabled | Qt.ItemIsSelectable
                   | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        else:
            res = (Qt.ItemIsEnabled | Qt.ItemIsDropEnabled)
        return res

    def mimeTypes(self):
        """ Метод для декларации MIME типов, поддерживаемых моделью. """
        types = QStringList()
        types << self.getMime('event') << self.getMime('team')
        return types

    def mimeData(self, indexes):
        """ Метод для конвертации объектов в поддерживаемый MIME формат. """
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
        """ Перегруженный метод базового класса. Под ролью понимаем зал. """
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

    # Поддержка Drag'n'Drop - конец секции

