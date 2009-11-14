#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re
from datetime import datetime, timedelta
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Event(object):

    """ Класс события. """

    def __init__(self, dt, duration, course, *args, **kwargs):
        self.dt = dt
        self.duration = duration
        self.course = course

    def __unicode__(self):
        return self.course

class EventStorage(QStandardItemModel):


    def __init__(self, work_hours, week_days,
                 quant=timedelta(minutes=30),
                 room_list=tuple(), parent=None):
        self.work_hours = work_hours
        begin_hour, end_hour = work_hours
        rows = end_hour - begin_hour
        cols = len(week_days)
        QStandardItemModel.__init__(self, rows, cols, parent)

        self.event_mime = 'application/x-calendar-event'

        self.rc2e = {} # (row, col, room): event
        self.e2rc = {} # (event, room): [(row, col), (row, col), ...]

        self.quant = quant
        self.multiplier = timedelta(hours=1).seconds / self.quant.seconds
        self.rooms = room_list

        # Горизонтальные метки
        self.setHorizontalHeaderLabels(QStringList(week_days))

        # Вертикальные метки
        i = 0
        for chunk in xrange(begin_hour, end_hour + 1):
            item = QStandardItem()
            item.setText('%i:00' % (chunk),)
            self.setVerticalHeaderItem(i, item)
            item = QStandardItem()
            item.setText('%i:30' % (chunk),)
            self.setVerticalHeaderItem(i+1, item)
            i += 2

#     def index(self, row, col, parent):
#         return None

#     def parent(self, index):
#         return index.parent

#     def rowCount(self, parent):
#         if parent:
#             return 0
#         else:
#             return None

#     def columnCount(self, parent):
#         if parent:
#             return 0
#         else:
#             return None

    def data(self, index, role):
        """ Перегруженный метод базового класса. Под ролью понимаем зал. """
        if not index.isValid():
            return QVariant()
        event = self.get_event_by_cell(index.row(), index.column(), role)
        if event:
            cells = self.get_cells_by_event(event, role)
            if cells:
                if cells[0] == (index.row(), index.column()):
                    event.type = 'head'
                elif cells[-1] == (index.row(), index.column()):
                    event.type = 'tail'
                else:
                    event.type = 'body'
        return QVariant(event)

    def setData(self, index, value, role):
        """ Перегруженный метод базового класса. Под ролью понимаем зал. """
        pass

    def get_event_by_cell(self, row, col, room):
        """ Получение события по указанным координатам. """
        event = self.rc2e.get( (row, col, room), None )
        return event

    def get_cells_by_event(self, event, room):
        """ Получение всех ячеек события. """
        return self.e2rc.get( (event, room), None )

    def datetime2rowcol(self, dt):
        row = (dt.hour - self.work_hours[0]) * self.multiplier
        col = dt.weekday()
        return (row, col)

    def may_insert(self, event, row, col):
        """ Метод для проверки возможности размещения события по указанным
        координатам. Возвращает список залов, которые предоставляют такую
        возможность. """
        result = []
        for room, color, id in self.rooms:
            free = []
            for i in xrange(event.duration.seconds / self.quant.seconds):
                free.append( self.rc2e.get( (row + i, col, room), None ) is None )
            if reduce( lambda x,y: x and y, free ):
                result.append( room )
        return result

    def insert(self, room, event):
        """ Метод регистрации нового события. """
        row, col = self.datetime2rowcol(event.dt)
        cells = []
        for i in xrange(event.duration.seconds / self.quant.seconds):
            cells.append( (row + i, col) )
            self.rc2e.update( { (row + i, col, room): event } )
        self.e2rc.update( { (event, room): cells } )

    def remove(self, event, room):
        """ Метод удаления информации о событии. """
        cell_list = self.get_cells_by_event(event, room)
        if cell_list:
            for row, col in cell_list:
                del( rc2e[ (row, col, room) ] )
            del( e2rc[ (event, room) ] )

    def move(self, row, col, room, event):
        """ Метод перемещения события по координатной сетке. """
        self.remove(event, room)
        self.insert(row, col, room, event)

    # Поддержка Drag'n'Drop - начало секции

    def supportedDropActions(self):
        """ Метод для определения списка DnD действий, поддерживаемых
        моделью. """
        print 'EventStorage::supportedDropActions'
        return Qt.CopyAction | Qt.MoveAction

    def flags(self, index):
        """ Метод для определения списка элементов, которые могут участвовать
        в DnD операциях. """
        #print 'EventStorage::flags'
        default_flags = QStandardItemModel.flags(self, index)
        if index.isValid(): # FIXME - сделать проверку
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | default_flags
        else:
            return Qt.ItemIsDropEnabled | default_flags

    def mimeTypes(self):
        """ Метод для декларации MIME типов, поддерживаемых моделью. """
        print 'EventStorage::mimeTypes'
        types = QStringList()
        types << self.event_mime
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

    def dropMimeData(self, data, action, row, column, parent):
        print 'EventStorage::dropMimeData'
        if action == Qt.IgnoreAction:
            return True
        if not data.hasFormat(self.event_mime):
            return False
        if column > 0:
            return False

        itemData = data.data(self.event_mime)
        dataStream = QDataStream(itemData, QIODevice.ReadOnly)

        id = QString()
        stream >> id

        print id



    #def removeRows()

    # Поддержка Drag'n'Drop - конец секции

class QtScheduleDelegate(QItemDelegate):

    """ Делегат для ячеек расписания. """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        self.parent = parent

    def paint(self, painter, option, index):
        """ Метод для отрисовки ячейки. """
        painter.save()

        model = index.model()
        rooms = model.rooms
        count = len(rooms)

        dx = self.parent.scrolledCellX
        dy = self.parent.scrolledCellY

        row = index.row()
        col = index.column()

        for room_name, room_color, room_id in rooms:
            event = model.data(index, room_id).toPyObject()
            if event:
                # заполняем тело события
                w = option.rect.width() / count
                h = option.rect.height()
                x = dx + col * (option.rect.width() + 1) + \
                    w * map(lambda x: x[2] == room_id, rooms).index(True)
                y = dy + row * (option.rect.height() + 1)
                painter.fillRect(x, y, w, h, self.parent.string2color(room_color));
                # готовимся рисовать границы
                pen = QPen(Qt.black)
                pen.setWidth(3)
                painter.setPen(pen)

                # отрисовываем элементы в зависимости от типа ячейки
                painter.drawLine(x, y+h, x, y)
                painter.drawLine(x+w, y+h, x+w, y)
                if event.type == 'head':
                    painter.drawLine(x, y, x+w, y)
                elif event.type == 'tail':
                    painter.drawLine(x, y+h, x+w, y+h)
                else:
                    pass
        painter.restore()
        #QItemDelegate.paint(self, painter, option, index)

class QtSchedule(QTableView):

    """ Класс календаря. """

    def __init__(self, *args):
        QTableView.__init__(self, *args)

        self.events = {}
        self.cells = {}
        self.scrolledCellX = 0
        self.scrolledCellY = 0

        self.rooms = [('red', '#ffaaaa', 100),
                      ('green', '#aaffaa', 101),
                      ('blue', '#aaaaff', 102)]

    def setup(self, work_hours, quant):
        self.work_hours = work_hours
        self.quant = quant

        self.model = EventStorage(
            self.work_hours,
            [ self.tr('Monday'), self.tr('Tuesday'),
              self.tr('Wednesday'), self.tr('Thursday'),
              self.tr('Friday'), self.tr('Saturday'),
              self.tr('Sunday') ],
            quant, self.rooms #[name for name, color, id in self.rooms]
            )
        self.setModel(self.model)

        # Тестовое заполнение модели
        min60 = timedelta(hours=1)
        min90 = timedelta(hours=1, minutes=30)
        min120 = timedelta(hours=2)

        test_data = [
            (100, Event(datetime(2009,11,2,12), min60, 'First')),
            (102, Event(datetime(2009,11,2,11), min90, 'Second')),
            (101, Event(datetime(2009,11,2,12), min60, 'Third')),
            (101, Event(datetime(2009,11,3,12), min60, 'Third')),
            (100, Event(datetime(2009,11,2,16), min120, 'Long')),
            ]
        for room, event in test_data:
            self.model.insert(room, event)

        print self.model.rc2e
        print self.model.e2rc

        # Запрещаем выделение множества ячеек
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Разрешаем принимать DnD
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop) #InternalMove

        # Запрещаем изменение размеров ячейки
        self.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setResizeMode(QHeaderView.Fixed)

        # Скроллинг
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Назначаем делегата для ячеек
        delegate = QtScheduleDelegate(self)
        self.setItemDelegate(delegate)

    def string2color(self, color):
        """ Метод для преобразования #RRGGBB в QColor. """
        regexp = re.compile(r'#(?P<red_component>[0-9a-f]{2})(?P<green_component>[0-9a-f]{2})(?P<blue_component>[0-9a-f]{2})')
        groups = re.match(regexp, color)
        if groups:
            return QColor(int(groups.group('red_component'), 16),
                          int(groups.group('green_component'), 16),
                          int(groups.group('blue_component'), 16))
        return None

    def scrollContentsBy(self, dx, dy):
        """ Обработчик скроллинга, см. QAbstractScrollArea. Накапливаем
        скроллинг по осям, в качестве единицы измерения используется
        пиксел. """
        # см. QAbstractItemView.ScrollMode
        if dx != 0:
            self.scrolledCellX += dx
        if dy != 0:
            self.scrolledCellY += dy
        QTableView.scrollContentsBy(self, dx, dy)

    def mousePressEvent(self, event):
        """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
        if event.button() == Qt.LeftButton:

            index = self.indexAt(event.pos())
            row = index.row()
            col = index.column()
            x = event.x() - self.scrolledCellX
            y = event.y() - self.scrolledCellY
            w = self.columnWidth(index.column())
            cx = self.columnViewportPosition(col) - self.scrolledCellX
            cy = self.rowViewportPosition(row) - self.scrolledCellY

            event_index = (x - cx) / (w / len(self.rooms))
            room_name, room_color, room_role = self.rooms[event_index]

            #Проверка наличия события в указанном месте.
            cal_event = self.model.get_event_by_cell(row, col, room_role)
            if not cal_event:
                return

            pixmap = QPixmap(100, 60)
            pixmap.fill(Qt.white)
            painter = QPainter(pixmap)
            painter.fillRect(2,2,96,56, self.string2color(room_color))

            pen = QPen(Qt.black)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(0, 0, 100, 60)

            painter.end()

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << QString('%i,%i,%i' % (row, col, room_role))
            mimeData = QMimeData()
            mimeData.setData(self.model.event_mime, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            if drag.start(Qt.MoveAction) == 0:
                print 'QtSchedule::mousePressEvent - DnD has ended successfully'

    def mouseMoveEvent(self, event):
        print 'QtSchedule::mouseMoveEvent'

    def dragEnterEvent(self, event):
        print 'QtSchedule::dragEnterEvent'
        if event.mimeData().hasFormat(self.model.event_mime):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        print 'QtSchedule::dragLeaveEvent'
        event.accept()

    def dragMoveEvent(self, event):
        #print 'QtSchedule::dragMoveEvent'
        if event.mimeData().hasFormat(self.model.event_mime):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print 'QtSchedule::dropEvent'
        if event.mimeData().hasFormat(self.model.event_mime):
            itemData = event.mimeData().data(self.model.event_mime)
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)
            coordinates = QString()
            dataStream >> coordinates
            (row, col, room_role) = [int(i) for i in coordinates.split(',')]

            event.setDropAction(Qt.MoveAction)
            event.accept()
            print 'format is', self.model.event_mime
            print 'coordinates are', (row, col, room_role)
        else:
            event.ignore()
            print 'unknown format'

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.setup_view()

        self.setWindowTitle(self.tr('Manager\'s interface'))
        self.resize(640, 480)

    def setup_view(self):
        splitter = QSplitter()
        self.schedule = QtSchedule(self)
        self.schedule.setup((8, 23), timedelta(minutes=30))

        splitter.addWidget(self.schedule)

        self.setCentralWidget(splitter)

    # Drag'n'Drop section begins
    def mousePressEvent(self, event):
        print 'press event', event.button()

    def mouseMoveEvent(self, event):
        print 'move event', event.pos()
    # Drag'n'Drop section ends

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
