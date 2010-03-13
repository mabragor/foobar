# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re
from datetime import datetime, timedelta

from http_ajax import HttpAjax
from event_storage import Event, EventStorage, EventTraining, EventRent

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

        self.current_event = None
        self.current_data = None
        self.selected_event = None
        self.selected_data = None

        # Запрещаем выделение множества ячеек
        self.setSelectionMode(QAbstractItemView.ExtendedSelection) #SingleSelection)

        # Разрешаем принимать DnD
#         self.setAcceptDrops(True)
#         self.setDragEnabled(True)
#         self.setDropIndicatorShown(True)

        #self.setDragDropMode(QAbstractItemView.DragDrop) #InternalMove

        # Запрещаем изменение размеров ячейки
        self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.connect(self.horizontalHeader(),
                     SIGNAL('sectionClicked(int)'),
                     self.expandDay)

        # Скроллинг
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setGridStyle(Qt.DotLine)
        self.resizeColumnsToContents()
        self.verticalHeader().setStretchLastSection(True)

        # Назначаем делегата для ячеек
        delegate = QtScheduleDelegate(self)
        self.setItemDelegate(delegate)

        # Контекстное меню
        self.ctxMenuExchange = QAction(_('Exchange rooms'), self)
        self.ctxMenuExchange.setStatusTip(_('Exchange rooms between selected and current events.'))
        self.connect(self.ctxMenuExchange, SIGNAL('triggered()'), self.exchangeRooms)
        self.contextMenu = QMenu(self)
        self.contextMenu.addAction(self.ctxMenuExchange)

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
        self.model().insert(room_id, event, True)

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

    def expandDay(self, section):
        self.model().changeShowMode(section)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)

    def data_of_event(self, event):
        """ Метод для получения информации по возникшему событию. """
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
        return (index, row, col, x, y, cx, cy,
                room_name, room_color, room_id)

    def event_intersection(self, event_a, event_b):
        """ Метод для определения пересечения событий по времени. """
        a1 = event_a.begin
        a2 = a1 + event_a.duration
        b1 = event_b.begin
        b2 = b1 + event_b.duration

        if a1 <= b1 < a2 <= b2:
            return True
        if b1 <= a1 < b2 <= a2:
            return True
        if a1 <= b1 < b2 <= a2:
            return True
        if b1 <= a1 < a2 <= b2:
            return True
        return False

    def contextMenuEvent(self, event):
        """ Обработчик контекстного меню. """
        index, row, col, x, y, cx, cy,\
            room_name, room_color, room_id \
            = self.data_of_event(event)

        #Проверка наличия события в указанном месте.
        self.current_event = self.model().get_event_by_cell(row, col, room_id)
        self.current_data = (row, col, room_id)
        if not self.current_event:
            return
        else:
            # запомнить текущее событие
            self.contextRow = index.row()

            self.ctxMenuExchange.setDisabled(False)

            # отключаем обмен, если:
            # - выбрано одно событие;
            # - даты событий не совпадают;
            # - дата любого события в прошлом
            if self.selected_event is None or \
                    not self.event_intersection(self.current_event, self.selected_event) or \
                    self.current_event == self.selected_event or \
                    self.current_event.begin.date() != self.selected_event.begin.date() or \
                    self.current_event.begin < datetime.now() or \
                    self.selected_event.begin < datetime.now():
                self.ctxMenuExchange.setDisabled(True)
            if 'week' != self.model().showMode:
                self.ctxMenuExchange.setDisabled(True)
            self.contextMenu.exec_(event.globalPos())

    def exchangeRooms(self):
        exchanged = self.model().exchangeRoom(self.current_data,
                                              self.selected_data)
        if exchanged:
            data = self.current_data
            self.current_data = self.selected_data
            self.selected_data = data
            self.parent.statusBar().showMessage(_('Complete.'))
        else:
            self.parent.statusBar().showMessage(_('Unable to exchange.'))

    def mousePressEvent(self, event):
        """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
        if event.button() == Qt.LeftButton:
            index, row, col, x, y, cx, cy,\
                room_name, room_color, room_id \
                = self.data_of_event(event)

            #Проверка наличия события в указанном месте.
            self.current_event = self.model().get_event_by_cell(row, col, room_id)
            if not self.current_event:
                return
            else:
                # Визуально выделяем отмеченное событие
                self.selected_event = self.current_event
                self.selected_data = (row, col, room_id)
                self.model().emit(SIGNAL('layoutChanged()'))

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

            #res = drag.start(Qt.CopyAction|Qt.MoveAction)
            #print 'QtSchedule::mousePressEvent', drop_action[res]

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
        evt = variant.toPyObject()
        self.parent.showEventProperties(evt, room_id)
        event.accept()

    def mouseMoveEvent(self, event):
        print 'QtSchedule::mouseMoveEvent'

    def dragEnterEvent(self, event):
        print 'QtSchedule::dragEnterEvent',
        if event.mimeData().hasFormat(self.getMime('event')) or \
                event.mimeData().hasFormat(self.getMime('team')):
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
                    event.mimeData().hasFormat(self.getMime('team')):
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        print 'QtSchedule::dropEvent',
        event_mime = self.getMime('event')
        team_mime = self.getMime('team')
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

        elif event.mimeData().hasFormat(team_mime):
            itemData = event.mimeData().data(team_mime)
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)
            team = QString()
            dataStream >> team
            #print team

            event.acceptProposedAction()

        else:
            event.ignore()
            print 'unknown format'

    def viewportEvent(self, event):
        """ Reimplement ToolTip Event. """
        if event.type() == QEvent.ToolTip and self.rooms:
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
            try:
                room_name, room_color, room_id = self.rooms[event_index]
                model = self.model()
                title = model.data(model.index(row, col), Qt.ToolTipRole, room_id).toString()
                if len(title) > 0:
                    QToolTip.showText(help.globalPos(), QString(title))
            except:
                pass
        return QTableView.viewportEvent(self, event)

#from settings import XPM_EVENT_CLOSED

class QtScheduleDelegate(QItemDelegate):

    """ Делегат для ячеек расписания. """

    HORIZONTAL = 0
    VERTICAL = 1
    PADDING = 2
    STEP = 5

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        self.parent = parent

    def prepare(self, painter, pen_tuple, brush=None):
        pen_color, pen_width = pen_tuple
        pen = QPen(pen_color)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        if brush is not None:
            brush_color = brush
            brush = QBrush(brush_color)
            painter.setBrush(brush)

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
            if isinstance(event, Event):
                # заполняем тело события
                w = option.rect.width() / count
                h = option.rect.height()
                x = dx + col * (option.rect.width() + 1) + \
                    w * map(lambda x: x[2] == room_id, rooms).index(True)
                y = dy + row * (option.rect.height() + 1)
                painter.fillRect(x, y, w, h, self.parent.string2color('#%s' % room_color));
                # готовимся рисовать границы
                if self.parent.selected_event == event:
                    self.prepare( painter, (Qt.blue, 3) )
                else:
                    self.prepare( painter, (Qt.black, 1) )

                # отрисовываем элементы в зависимости от типа ячейки
                painter.drawLine(x, y+h, x, y)
                painter.drawLine(x+w, y+h, x+w, y)
                if event.show_type == 'head':
                    painter.drawLine(x, y, x+w, y)
                elif event.show_type == 'tail':
                    painter.drawLine(x, y+h, x+w, y+h)
                else:
                    pass

                # тип события: тренировка, аренда
                if isinstance(event, EventRent) and event.show_type == 'tail':
                    self.prepare( painter, (Qt.black, 1), Qt.blue )
                    lower = w if w < h else h
                    SIDE = int(lower / 4)
                    rw = rh = SIDE if lower > SIDE else lower-2
                    rx = x+w-rw-1
                    ry = y+h-rh-1
                    painter.drawRect(rx, ry, rw, rh)

                if isinstance(event, EventTraining) and event.show_type == 'tail':
                    if event.fixed in (1, 2):
                        if event.fixed == 1:
                            self.prepare( painter, (Qt.green, 3) )
                        if event.fixed == 2:
                            self.prepare( painter, (Qt.blue, 3) )
                        painter.drawLine(x+self.PADDING, y+h-self.PADDING-5,
                                         x+self.PADDING+5, y+h-self.PADDING)

                line_dir = self.direction(w, h)
                if event.status == 1:
                    self.prepare( painter, (Qt.red, 3) )
                    if self.HORIZONTAL == line_dir:
                        if event.show_type == 'head':
                            painter.drawLine(x+self.PADDING, y+(self.STEP*1),
                                             x+w-self.PADDING, y+(self.STEP*1))
                    else:
                        painter.drawLine(x+(self.STEP*1), y+self.PADDING,
                                         x+(self.STEP*1), y+h-self.PADDING)
                elif event.status == 2:
                    self.prepare( painter, (self.parent.string2color('#888888'), 3) )
                    if self.HORIZONTAL == line_dir:
                        if event.show_type == 'head':
                            painter.drawLine(x+self.PADDING, y+(self.STEP*2),
                                             x+w-self.PADDING, y+(self.STEP*2))
                    else:
                        painter.drawLine(x+(self.STEP*2), y+self.PADDING,
                                         x+(self.STEP*2), y+h-self.PADDING)
                    #painter.drawPixmap(x+3, y+3, 8, 8, QPixmap(XPM_EVENT_CLOSED))

        painter.restore()
        #QItemDelegate.paint(self, painter, option, index)

    def direction(self, width, height):
        return self.HORIZONTAL if width < height else self.VERTICAL
