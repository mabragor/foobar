# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, date, timedelta

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')
__ = lambda x: datetime(*time.strptime(str(x), '%Y-%m-%d %H:%M:%S')[:6])

from settings import userRoles
from http_ajax import HttpAjax

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Event(object):

    """ Класс события. """

    def __init__(self, id, begin, duration, status):
        self.schedule_id = id
        self.begin = begin
        self.duration = duration
        self.status = status

    def __unicode__(self):
        return self.title

    @property
    def id(self):
        return self.schedule_id

    @property
    def event_id(self):
        return self.event['id']

    @property
    def title(self):
        return self.event['title']

class EventTraining(Event):

    """ Класс тренировки. """

    def __init__(self, course, schedule_id, begin, duration, status):
        Event.__init__(self, schedule_id, begin, duration, status)
        self.type = 'training'
        self.event = course

class EventRent(Event):

    """ Класс аренды. """

    def __init__(self, rent, schedule_id, begin, duration, status):
        Event.__init__(self, schedule_id, begin, duration, status)
        self.type = 'rent'
        self.event = rent

class EventStorage(QAbstractTableModel):

    def __init__(self, work_hours,
                 quant=timedelta(minutes=30),
                 room_list=tuple(), parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.parent = parent
        self.work_hours = work_hours
        self.quant = quant
        self.rooms = room_list
        self.multiplier = timedelta(hours=1).seconds / self.quant.seconds

        self.getMime = parent.getMime

        self.week_days = [ _('Monday'), _('Tuesday'),
              _('Wednesday'), _('Thursday'),
              _('Friday'), _('Saturday'),
              _('Sunday') ]

        begin_hour, end_hour = work_hours
        self.rows_count = (end_hour - begin_hour) * timedelta(hours=1).seconds / quant.seconds
        self.cols_count = len(self.week_days)

        self.initModel()
        self.showCurrWeek()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return self.rows_count

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return self.cols_count

    def initModel(self):
        self.rc2e = {} # (row, col, room): event
        self.e2rc = {} # (event, room): [(row, col), (row, col), ...]

    def showCurrWeek(self):
        now = datetime.now()
        self.weekRange = self.date2range(now)
        self.loadData(now)
        return self.weekRange

    def showPrevWeek(self):
        current_monday, current_sunday = self.weekRange
        prev_monday = current_monday - timedelta(days=7)
        self.loadData(prev_monday)
        return self.weekRange

    def showNextWeek(self):
        current_monday, current_sunday = self.weekRange
        next_monday = current_monday + timedelta(days=7)
        self.loadData(next_monday)
        return self.weekRange

    def loadData(self, d):
        self.initModel()
        self.parent.statusBar().showMessage(_('Request information for the calendar.'))
        monday, sunday = week_range = self.date2range(d)
	ajax = HttpAjax(self.parent, '/manager/get_week/',
                        {'monday': monday,
                         'filter': []})
	if ajax:
            self.parent.statusBar().showMessage(_('Parsing the response...'))
	    response = ajax.parse_json()
            self.parent.statusBar().showMessage(_('Filling the calendar...'))
            for e in response['events']:
                begin = __(e['begin'])
                end = __(e['end'])
                duration = end - begin
                event = EventTraining(e['event'], e['id'], begin, duration, e['status'])
                self.insert( int(e['room']['id']), event )
            self.weekRange = week_range
            self.emit(SIGNAL('layoutChanged()'))
            self.parent.statusBar().showMessage(_('Done'), 2000)
            return True
	return False

    def headerData(self, section, orientation, role):
        """ Метод для определения вертикальных и горизонтальных меток для
        рядов и колонок таблицы. """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            mon, sun = self.weekRange
            daystr = (mon + timedelta(days=section)).strftime('%d/%m')
            return QVariant('%s\n%s' % (self.week_days[section], daystr))
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
        event = self.get_event_by_cell(index.row(), index.column(), room_id)
        if event:
            if role == Qt.ToolTipRole:
                return QVariant(event.title)
            if role == Qt.DisplayRole:
                cells = self.get_cells_by_event(event, room_id)
                if cells:
                    if cells[0] == (index.row(), index.column()):
                        event.show_type = 'head'
                    elif cells[-1] == (index.row(), index.column()):
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
        return self.rc2e.get( (row, col, room_id), None )

    def get_cells_by_event(self, event, room_id):
        """ Получение всех ячеек события. """
        return self.e2rc.get( (event, room_id), None )

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
        return (row, col)

    def may_insert(self, event, row, col):
        """ Метод для проверки возможности размещения события по указанным
        координатам. Возвращает список залов, которые предоставляют такую
        возможность.

        Для каждого зала из списка проверить наличие свободных
        интервалов времени.
        """
        result = []
        for room_name, room_color, room_id in self.rooms:
            free = []
            for i in xrange(event.duration.seconds / self.quant.seconds):
                free.append( self.rc2e.get( (row + i, col, room_id), None ) is None )
            print free

            if reduce( lambda x,y: x and y, free ):
                result.append(room_id)
        return result

    def insert(self, room_id, event, emit_signal=False):
        """ Метод регистрации нового события. """
        self.emit(SIGNAL('layoutAboutToBeChanged()'))

        row, col = self.datetime2rowcol(event.begin)
        #self.beginInsertRows(QModelIndex(), row, row)
        cells = []
        for i in xrange(event.duration.seconds / self.quant.seconds):
            cells.append( (row + i, col) )
            self.rc2e.update( { (row + i, col, room_id): event } )
        self.e2rc.update( { (event, room_id): cells } )
        #self.endInsertRows()

        if emit_signal:
            self.emit(SIGNAL('layoutChanged()'))

    def remove(self, event, room):
        """ Метод удаления информации о событии. """
        cell_list = self.get_cells_by_event(event, room)
        if cell_list:
            for row, col in cell_list:
                del( self.rc2e[ (row, col, room) ] )
            del( self.e2rc[ (event, room) ] )
            self.emit(SIGNAL('layoutChanged()'))

    def move(self, row, col, room, event):
        """ Метод перемещения события по координатной сетке. """
        self.remove(event, room)
        self.insert(row, col, room, event)

    # Поддержка Drag'n'Drop - начало секции

    def supportedDropActions(self):
        """ Метод для определения списка DnD действий, поддерживаемых
        моделью. """
        print 'EventStorage::supportedDropActions'
        return (Qt.CopyAction | Qt.MoveAction)

    def flags(self, index):
        """ Метод для определения списка элементов, которые могут участвовать
        в DnD операциях. """
        #print 'EventStorage::flags', index.row(), index.column()
        if index.isValid():
            res = (Qt.ItemIsEnabled | Qt.ItemIsSelectable
                   | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        else:
            res = (Qt.ItemIsEnabled | Qt.ItemIsDropEnabled)
        return res

    def mimeTypes(self):
        """ Метод для декларации MIME типов, поддерживаемых моделью. """
        print 'EventStorage::mimeTypes'
        types = QStringList()
        types << self.getMime('event') << self.getMime('course')
        return types

    def mimeData(self, indexes):
        """ Метод для конвертации объектов в поддерживаемый MIME формат. """
        print 'EventStorage::mimeData'
        mimeData = QMimeData()
        encodedData = QByteArray()

        stream = QDataStream(encodedData, QIODevice.WriteOnly)

        events = []

        print indexes

        for index in indexes:
            if index.isValid():
                print dir(index)
                print self.data(index, 100)

        mimeData.setData(self.getMime('event'), encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        print 'EventStorage::dropMimeData'
        if action == Qt.IgnoreAction:
            return True

        event_mime = self.getMime('event')
        course_mime = self.getMime('course')

        if not data.hasFormat(event_mime) and \
                not data.hasFormat(course_mime):
            print 'badmime'
            return False
        if column > 0:
            return False

        itemData = data.data(event_mime)
        dataStream = QDataStream(itemData, QIODevice.ReadOnly)

        id = QString()
        stream >> id

        print id
        return True

    def setData(self, index, value, role):
        """ Перегруженный метод базового класса. Под ролью понимаем зал. """
        print 'EventStorage::setData'
        return True

    def setHeaderData(self, section, orientation, value, role):
        print 'EventStorage::setHeaderData'
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

