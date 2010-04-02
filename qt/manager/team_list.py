# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from settings import _, DEBUG

from PyQt4.QtGui import *
from PyQt4.QtCore import *

CARD_TYPE = [_('Normal'), _('Club')]

class TeamListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        # хранилище данных модели
        self.storage = []

        self.labels = [_('Title'), _('Price'), _('Paid'),
                       _('Card'), _('Sold'), _('Used'),
                       _('Assigned'), _('Begin'), _('Expired'), _('Cancelled'),
                       'id', 'team_id']
        self.model_fields = ['title', 'price', 'paid',
                             'card_type', 'count_sold', 'count_used',
                             'reg_date', 'bgn_date', 'exp_date', 'cnl_date',
                             'id', 'team_id']

    def initData(self, client_id, data):
        """
        Формат полученных данных: см. методы about() у моделей.
        """
        self.client_id = client_id
        for rec in data:
            if type(rec) is not dict:
                raise 'Check format'
            team = rec['team']
            self.storage.append( [
                team['title'],
                rec['price'],
                rec['paid'],
                rec['type'],
                rec['sold'],
                rec['used'],
                rec['register'],
                rec['begin'],
                rec['expire'],
                rec['cancel'],
                rec['id'],
                team['id']
                ] )
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

#         self.emit(SIGNAL('columnsInserted(QModelIndex, int, int)'),
#                   QModelIndex(), 1, cols)
#         self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
#                   self.createIndex(0, 0),
#                   self.createIndex(self.rowCount(), self.columnCount()))

    def get_model_as_formset(self):
        formset = {
            'form-TOTAL_FORMS': str(len(self.storage)),
            'form-INITIAL_FORMS': u'0',
            }
        for record in self.storage:
            index = self.storage.index(record)

            title, price, paid, type_id, sold, used, register,\
                begin, expire, cancel, card_id, team_id = record

            row = {
                'form-%s-client_id' % index: self.client_id,
                'form-%s-card_id' % index: card_id,
                'form-%s-team_id' % index: team_id,
                'form-%s-paid' % index: paid,
                'form-%s-type_id' % index: type_id,
                'form-%s-sold' % index: sold,
                'form-%s-begin' % index: begin,
                'form-%s-expire' % index: expire,
                }
            formset.update( row )
        return formset

    def rowCount(self, parent=None): # base class method
        if parent and parent.isValid():
            return 0
        else:
            return len(self.storage)

    def columnCount(self, parent=None):# base class method
        if parent and parent.isValid():
            return 0
        else:
            return len(self.labels) - 2

    def modelColumnCount(self):
        return len(self.model_fields)

    def headerData(self, section, orientation, role): # base class method
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section+1) # порядковый номер
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def _dtapply(self, value):
        if value is not None:
            if type(value) in [date, datetime]:
                return value
            if type(value) is str:
                if len(value) == 10:
                    result = datetime.strptime(value, '%Y-%m-%d')
                else:
                    result = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return result.date()
            print 'dtapply', value
            raise RuntimeWarning
        else:
            return None

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole) :
            return QVariant()
        idx_row = index.row()
        idx_col = index.column()
        record = list(self.storage[idx_row])

        # Warning! This tuple describes field value types.
        # Look at TeamListDelegate! These tuples must be synced.
        map = ( unicode, # title
                float, # price
                float, # paid
                lambda x: CARD_TYPE[int(x)], # card type
                int, # sold
                int, # used
                self._dtapply, # registered
                self._dtapply, # begin
                self._dtapply, # expire
                self._dtapply, # cancelled
                int, # record id
                int # team id
                )

        object_type = map[idx_col]
        try:
            value = record[idx_col]
        except IndexError:
            return QVariant() # запись в модели ещё не заполнена

        if value is None:
            return QVariant() # пустое значение
        else:
            return QVariant(object_type(value))

    def setRow(self, index, record, role, card_type=1,
               bgn_date=date.today(), duration_index=0):
        if index.isValid() and role == Qt.EditRole:
            today = date.today()
            reg_date = today
            if card_type == 0:
                exp_date = bgn_date + timedelta(days=30)
            else:
                deltas = (relativedelta(months=+3), #0
                          relativedelta(months=+6), #1
                          relativedelta(months=+9), #2
                          relativedelta(months=+12), #3
                      )
                exp_date = bgn_date + deltas[duration_index]
            title, team_id, count, price, coach, duration = record
            paid = 0
            record = [title, price, paid, card_type, count, 0,
                      reg_date, bgn_date, exp_date, None, 0, team_id]

            idx_row = index.row()
            idx_col = 0
            for i in record:
                self.setData(self.createIndex(idx_row, idx_col), i, role)
                idx_col += 1

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = index.column()
            print '[%i, %i] %s' % (idx_row, idx_col, value)

            record = list(self.storage[idx_row])
            if len(record) == 0: # init record in this case
                for i in xrange(self.modelColumnCount()):
                    record.append(None)

            # FIXME: I guess no convert is needed.
            if type(value) is QVariant:
                v = value.toString()
            else:
                v = value

            #print type(value), value
            record[idx_col] = v
            self.storage[idx_row] = tuple(record)

#             for item in self.storage:
#                 print '\t',
#                 for col in item:
#                     print col,
#                 print

            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            self.storage.insert(0, tuple())
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            del(self.storage[position + i])
        self.endRemoveRows()
        return True

class TeamListDelegate(QItemDelegate):

    """ The delegate allow to user to change the model values. """

    # Warning! This tuple describes field value types.
    # Look at TeamList::data method! These tuples must be synced.
    map = ( None, # title
            None, # price
            QLineEdit, # paid
            QComboBox, # card type
            QLineEdit, # sold
            None, # used
            None, # registered
            QDateEdit, # begin
            QDateEdit, # expire
            None, # cancelled
            None, # record id
            None # team id
            )

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        print 'TeamListDelegate: constructor'

#     def eventFilter(obj, event):
#         print 'event type', event.type()

    def createEditor(self, parent, option, index):
        print 'TeamListDelegate: createEditor'
        delegate_editor = self.map[ index.column() ]
        if delegate_editor:
            return delegate_editor(parent)
        else:
            return None

    def setEditorData(self, editor, index):
        print 'TeamListDelegate: setEditorData'
        raw_value = index.model().data(index, Qt.DisplayRole)

        delegate_editor = self.map[ index.column() ]
        if not delegate_editor or delegate_editor is QLineEdit:
            value = raw_value.toString()
            editor.setText(value)
        elif delegate_editor is QComboBox:
            for i in CARD_TYPE:
                editor.addItem( i, QVariant(CARD_TYPE.index(i)) )
            value = raw_value.toString()
            item_index = editor.findText(value)
            editor.setCurrentIndex( item_index )
        elif delegate_editor is QDateEdit:
            value = raw_value.toDate()
            editor.setDate(value)
        else:
            return None

    def setModelData(self, editor, model, index):
        print 'TeamListDelegate: setModelData'
        # ??? lineEdit.interpretText()

        delegate_editor = self.map[ index.column() ]
        if not delegate_editor or delegate_editor is QLineEdit:
            value = editor.text()
        elif delegate_editor is QComboBox:
            value = editor.currentIndex()
        elif delegate_editor is QDateEdit:
            value = str(editor.date().toPyDate())
            print 'delegate setModelData', value, type(value)
        else:
            value = 'Not implemented'
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        print 'TeamListDelegate: updateEditorGeometry'
        editor.setGeometry(option.rect)

class TeamList(QTableView):

    """ Класс списка курсов. """

    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        #self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        #self.resizeColumnsToContents()

        self.actionTeamCancel = QAction(_('Cancel team'), self)
        self.actionTeamCancel.setStatusTip(_('Cancel current team.'))
        self.connect(self.actionTeamCancel, SIGNAL('triggered()'), self.teamCancel)

        self.delegate = TeamListDelegate()
        self.setItemDelegate(self.delegate)

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             index = self.indexAt(event.pos())
#             print index.row()

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self.contextRow = index.row()
        menu = QMenu(self)
        menu.addAction(self.actionTeamCancel)
        menu.exec_(event.globalPos())

    def teamCancel(self):
        if DEBUG:
            print 'canceled [%i]' % self.contextRow
