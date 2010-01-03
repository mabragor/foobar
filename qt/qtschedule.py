# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re
from datetime import datetime, timedelta

from event_storage import Event, EventStorage

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class QtSchedule(QTableView):

    """ Класс календаря. """

    def __init__(self, work_hours, quant, rooms, parent=None):
        QTableView.__init__(self, parent)

        self.parent = parent
        self.events = {}
        self.cells = {}
        self.rooms = rooms
        self.scrolledCellX = 0
        self.scrolledCellY = 0

        self.getMime = parent.getMime

        self.work_hours = work_hours
        self.quant = quant

        # Запрещаем выделение множества ячеек
        self.setSelectionMode(QAbstractItemView.ExtendedSelection) #SingleSelection)

        # Разрешаем принимать DnD
#         self.setAcceptDrops(True)
#         self.setDragEnabled(True)
#         self.setDropIndicatorShown(True)

        #self.setDragDropMode(QAbstractItemView.DragDrop) #InternalMove

        # Запрещаем изменение размеров ячейки
        self.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setResizeMode(QHeaderView.Fixed)

        # Скроллинг
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setGridStyle(Qt.DotLine)
        self.resizeColumnsToContents()
        self.verticalHeader().setStretchLastSection(True)

        # Назначаем делегата для ячеек
        delegate = QtScheduleDelegate(self)
        self.setItemDelegate(delegate)

    def string2color(self, color):
        """ Метод для преобразования #RRGGBB в QColor. """
        regexp = re.compile(r'#(?P<red_component>[0-9a-fA-F]{2})(?P<green_component>[0-9a-fA-F]{2})(?P<blue_component>[0-9a-fA-F]{2})')
        groups = re.match(regexp, color)
        if groups:
            return QColor(int(groups.group('red_component'), 16),
                          int(groups.group('green_component'), 16),
                          int(groups.group('blue_component'), 16))
        return None

    def get_scrolled_coords(self, rel_x, rel_y):
        """ Метод вычисляет абсолютные координаты по относительным, учитываю
        позицию скроллера. """
        abs_x = rel_x - self.scrolledCellX
        abs_y = rel_y - self.scrolledCellY
        return (abs_x, abs_y)

    def get_cell_coords(self, abs_x, abs_y):
        """ Метод определяет какой ячейке (row, col) принадлежат
        координаты. """
        return (self.rowAt(abs_y), self.columnAt(abs_x))

    def insertEvent(self, room_id, event):
        self.model().insert(room_id, event)

    def cellRowColRelative(self, rel):
        """ Метод определяет какой ячейке принадлежат переданные координаты,
        принимая во внимание текущую позицию скроллера. """
        if type(rel) is tuple:
            rel_x, rel_y = rel
            abs_x = rel_x - self.scrolledCellX
            abs_y = rel_y - self.scrolledCellY
        elif type(rel) is QPoint:
            abs_x = rel.x() - self.scrolledCellX
            abs_y = rel.y() - self.scrolledCellY
        return (self.rowAt(abs_y), self.columnAt(abs_x))

    def emptyRoomAt(self, (row_col)):
        """ Метод возвращает список свободных залов в данной ячейке. """
        row, col = row_col
        free = []
        for room_name, room_color, room_id in self.rooms:
            event = self.model().get_event_by_cell(row, col, room_id)
            if not event:
                free.append(id)
        return free

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
            cx, cy = self.get_scrolled_coords(self.columnViewportPosition(col),
                                              self.rowViewportPosition(row))
            event_index = (x - cx) / (w / len(self.rooms))
            room_name, room_color, room_id = self.rooms[event_index]

            #Проверка наличия события в указанном месте.
            cal_event = self.model().get_event_by_cell(row, col, room_id)
            if not cal_event:
                return

            pixmap = QPixmap(100, 60)
            pixmap.fill(Qt.white)
            painter = QPainter(pixmap)
            painter.fillRect(2,2,96,56, self.string2color('#%s' % room_color))

            pen = QPen(Qt.black)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(0, 0, 100, 60)

            painter.end()

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << QString('%i,%i,%i' % (row, col, room_id))
            mimeData = QMimeData()
            mimeData.setData(self.getMime('event'), itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)

            drop_action = {
                0: 'Qt::IgnoreAction',
                1: 'Qt::CopyAction',
                2: 'Qt::MoveAction',
                4: 'Qt::LinkAction',
                255: 'Qt::ActionMask',
                }

            res = drag.start(Qt.CopyAction|Qt.MoveAction)
            print 'QtSchedule::mousePressEvent', drop_action[res]

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        row = index.row()
        col = index.column()
        x = event.x() - self.scrolledCellX
        y = event.y() - self.scrolledCellY
        w = self.columnWidth(col)
        cx, cy = self.get_scrolled_coords(self.columnViewportPosition(col),
                                          self.rowViewportPosition(row))
        event_index = (x - cx) / (w / len(self.rooms))
        room_name, room_color, room_id = self.rooms[event_index]
        model = self.model()
        variant = model.data(model.index(row, col), Qt.DisplayRole, room_id)
        if not variant.isValid():
            return
        cal_event = variant.toPyObject()
        self.parent.showEventProperties(cal_event, room_id)
        event.accept()

    def mouseMoveEvent(self, event):
        print 'QtSchedule::mouseMoveEvent'

    def dragEnterEvent(self, event):
        print 'QtSchedule::dragEnterEvent',
        if event.mimeData().hasFormat(self.getMime('event')) or \
                event.mimeData().hasFormat(self.getMime('course')):
            event.acceptProposedAction()
            print 'accept'
        else:
            event.ignore()
            print 'ignore'

    def dragMoveEvent(self, event):
        """ Метод вызывается во время Drag'n'Drop. Здесь следует осуществлять
        проверку возможности скидывания перетаскиваемого объекта на текущую
        ячейку. """
        drop_cell = self.cellRowColRelative(event.pos())
        free_rooms = self.emptyRoomAt(drop_cell)

        if len(free_rooms) > 0:
            QTableView.dragMoveEvent(self, event)
            if event.mimeData().hasFormat(self.getMime('event')) or \
                    event.mimeData().hasFormat(self.getMime('course')):
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        print 'QtSchedule::dropEvent',
        event_mime = self.getMime('event')
        course_mime = self.getMime('course')
        if event.mimeData().hasFormat(event_mime):
            itemData = event.mimeData().data(event_mime)
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)
            coordinates = QString()
            dataStream >> coordinates
            (row, col, room_id) = [int(i) for i in coordinates.split(',')]

            event.acceptProposedAction()
            print event_mime, 'is dragged from', (row, col, room_id)
            drop_cell = self.cellRowColRelative(event.pos())
            print self.emptyRoomAt(drop_cell)

        elif event.mimeData().hasFormat(course_mime):
            itemData = event.mimeData().data(course_mime)
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)
            course = QString()
            dataStream >> course
            #print course

            event.acceptProposedAction()

        else:
            event.ignore()
            print 'unknown format'

    def viewportEvent(self, event):
        """ Reimplement ToolTip Event. """
        if event.type() == QEvent.ToolTip:
            help = QHelpEvent(event)
            index = self.indexAt(help.pos())
            row = index.row()
            col = index.column()
            x = help.x() - self.scrolledCellX
            y = help.y() - self.scrolledCellY
            w = self.columnWidth(col)
            cx, cy = self.get_scrolled_coords(self.columnViewportPosition(col),
                                              self.rowViewportPosition(row))
            event_index = (x - cx) / (w / len(self.rooms))
            room_name, room_color, room_id = self.rooms[event_index]
            model = self.model()
            title = model.data(model.index(row, col), Qt.ToolTipRole, room_id).toString()
            if len(title) > 0:
                QToolTip.showText(help.globalPos(), QString(title))
        return QTableView.viewportEvent(self, event)

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
            event = model.data(index, Qt.DisplayRole, room_id).toPyObject()
            if type(event) is Event:
                # заполняем тело события
                w = option.rect.width() / count
                h = option.rect.height()
                x = dx + col * (option.rect.width() + 1) + \
                    w * map(lambda x: x[2] == room_id, rooms).index(True)
                y = dy + row * (option.rect.height() + 1)
                painter.fillRect(x, y, w, h, self.parent.string2color('#%s' % room_color));
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
