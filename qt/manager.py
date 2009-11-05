#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys
from datetime import datetime, timedelta
from PyQt4 import QtGui, QtCore

class Event(object):

    """ Класс события. """

    def __init__(self, dt, duration, course, *args, **kwargs):
        self.dt = dt
        self.duration = duration
        self.course = course

    def __unicode__(self):
        return self.course

class QtScheduleDelegate(QtGui.QItemDelegate):

    """ Делегат для ячеек расписания. """

    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent

    def paint(self, painter, option, index):
        """ Метод для отрисовки ячейки. """
        painter.save()
        events = self.parent.events
        cells = self.parent.cells
        rooms = self.parent.rooms
        count = self.parent.room_count()
        dx = self.parent.scrolledCellX
        dy = self.parent.scrolledCellY

        row = index.row()
        col = index.column()
        if (row, col) in cells:
            rooms_info = cells[ (row, col) ]
            for key in rooms_info:
                # заполняем тело события
                w = option.rect.width() / count
                h = option.rect.height()
                x = (dx + col) * (option.rect.width() + 1) + \
                    w * map(lambda x: x[0] == key, rooms).index(True)
                y = (dy + row) * (option.rect.height() + 1)
                painter.fillRect(x, y, w, h, getattr(QtCore.Qt, key));
                # готовимся рисовать границы
                pen = QtGui.QPen(QtCore.Qt.black)
                pen.setWidth(2)
                painter.setPen(pen)
                # отрисовываем элементы в зависимости от типа ячейки
                event_id, cell_type = rooms_info[key]
                painter.drawLine(x, y+h, x, y)
                painter.drawLine(x+w, y+h, x+w, y)
                if cell_type == 'head':
                    painter.drawLine(x, y, x+w, y)
                elif cell_type == 'tail':
                    painter.drawLine(x, y+h, x+w, y+h)
                else:
                    pass
        painter.restore()
        QtGui.QItemDelegate.paint(self, painter, option, index)

class QtSchedule(QtGui.QTableView):

    """ Класс календаря. """

    def __init__(self, *args):
        QtGui.QTableView.__init__(self, *args)

        self.events = {}
        self.cells = {}
        self.scrolledCellX = 0
        self.scrolledCellY = 0

        self.rooms = [('red', '#ffaaaa'), ('green', '#aaffaa'), ('blue', '#aaaaff')]

    def setup(self, work_hours, quant):
        self.work_hours = work_hours
        self.quant = quant
        self.setup_model()
        self.setModel(self.model)

        # Запрещаем выделение множества ячеек
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        # Разрешаем принимать DnD
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        # Запрещаем изменение размеров ячейки
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

        # Назначаем делегата для ячеек
        delegate = QtScheduleDelegate(self)
        self.setItemDelegate(delegate)

    def setup_model(self):
        self.model = QtGui.QStandardItemModel(
            self.work_hours[1] - self.work_hours[0],
            7)
        # horizontal labels
        week_days = [ self.tr('Monday'), self.tr('Tuesday'),
                      self.tr('Wednesday'), self.tr('Thursday'),
                      self.tr('Friday'), self.tr('Saturday'),
                      self.tr('Sunday') ]
        self.model.setHorizontalHeaderLabels(QtCore.QStringList(week_days))
        # vertical labels
        i = 0
        for chunk in xrange(self.work_hours[0], (self.work_hours[1] + 1)):
            item = QtGui.QStandardItem()
            item.setText('%i:00' % (chunk),)
            self.model.setVerticalHeaderItem(i, item)
            item = QtGui.QStandardItem()
            item.setText('%i:30' % (chunk),)
            self.model.setVerticalHeaderItem(i+1, item)
            i += 2

    def datetime2rowcol(self, dt):
        multiplier = timedelta(hours=1).seconds / self.quant.seconds
        row = (dt.hour - self.work_hours[0]) * multiplier
        col = dt.weekday()
        return (row, col)

    def rowcol2datetime(self, row, column):
        pass

    def room_color(self, room_name):
        return filter(lambda x: x[0].lower() == room_name.lower(),
                      self.rooms)[0][1]

    def room_count(self):
        return len(self.rooms)

    def fill_cells(self, row, col, cell_count):
        """ Метод генерирует список ячеек для события, указывая их тип. """
        result = []
        rows_list = range(row, row+cell_count)
        for i in rows_list:
            if i == rows_list[0]: # первый элемент
                cell_type = 'head'
            elif i == rows_list[-1]: # последний элемент
                cell_type = 'tail'
            else: # остальные
                cell_type = 'body'
            result.append( (i, col, cell_type) )
        return result

    def set_event(self, room, event):
        """ Добавление события на календарь. """
        # генерируем уникальный идентификатор
        import uuid
        event_id = uuid.uuid4().hex

        # сохраняем событие
        self.events.update( { event_id: event.course } )

        # определяем используемые ячейки
        cell_count = event.duration.seconds / self.quant.seconds
        row, col = rowcol = self.datetime2rowcol(event.dt)

        cell_info = self.fill_cells(row, col, cell_count)
        for i in cell_info:
            cell_row, cell_col, cell_type = i

            if (cell_row, cell_col) not in self.cells:
                # создаём
                self.cells.update( { (cell_row, cell_col):
                                     { room: (event_id, cell_type) } } )
            else:
                # добавляем
                eventdict = self.cells[ (cell_row, cell_col) ]
                eventdict.update( { room: (event_id, cell_type) } )
                self.cells.update( { (cell_row, cell_col): eventdict } )

    def get_events(self):
        return self.events

    def scrollContentsBy(self, dx, dy):
        """ Обработчик скроллинга, см. QAbstractScrollArea. Накапливаем
        скроллинг по осям, в качестве единицы измерения используется
        ячейка. """
        # см. QAbstractItemView.ScrollMode
        if dx != 0:
            self.scrolledCellX += dx
        if dy != 0:
            self.scrolledCellY += dy
        QtGui.QTableView.scrollContentsBy(self, dx, dy)

    def mousePressEvent(self, event):
        """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
        if event.button() == QtCore.Qt.LeftButton:
            print event.pos()
            plainText = QtCore.QString('test')

            mimeData = QtCore.QMimeData()
            mimeData.setText(plainText)

            pixmap = QtGui.QPixmap(100, 60)
            pixmap.fill(QtCore.Qt.white)
            painter = QtGui.QPainter(pixmap)
            painter.fillRect(2,2,96,56, QtCore.Qt.gray)

            # готовимся рисовать границы
            pen = QtGui.QPen(QtCore.Qt.black)
            pen.setWidth(2)
            painter.setPen(pen)
            # отрисовываем элементы в зависимости от типа ячейки
            painter.drawRect(0, 0, 100, 60)

            painter.end()

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)

            drag.start()

    def mouseMoveEvent(self, event):
        print 'qtableview: move event', event.pos()

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.setup_view()

        self.setWindowTitle(self.tr('Manager\'s interface'))
        self.resize(640, 480)

        self.schedule.set_event('red',
                                Event(datetime(2009,11,2,12),
                                      timedelta(hours=1),
                                      'First'))
        self.schedule.set_event('blue',
                                Event(datetime(2009,11,2,11),
                                      timedelta(hours=1, minutes=30),
                                      'Second'))
        self.schedule.set_event('green',
                                Event(datetime(2009,11,2,12),
                                      timedelta(hours=1),
                                      'Third'))
        self.schedule.set_event('green',
                                Event(datetime(2009,11,3,12),
                                      timedelta(hours=1),
                                      'Third'))
        self.schedule.set_event('red',
                                Event(datetime(2009,11,2,16),
                                      timedelta(hours=2),
                                      'First'))
        print self.schedule.get_events()

    def setup_view(self):
        splitter = QtGui.QSplitter()
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
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
