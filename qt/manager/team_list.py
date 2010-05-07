# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from settings import _, DEBUG

from PyQt4.QtGui import *
from PyQt4.QtCore import *

PAID_STATUS = [_('Reserved'),
               _('Piad partially'),
               _('Paid')]
CARD_TYPE = [_('Normal'), _('Club')]
DURATION_TYPE = [_('30 days'), _('3 months'), _('6 months'),
                 _('9 months'), _('12 months')]

def _dtapply(value):
    if value is not None:
        if type(value) in [date, datetime]:
            return value
        if type(value) is str:
            if len(value) == 10:
                result = datetime.strptime(value, '%Y-%m-%d')
            else:
                result = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return result.date()
        raise RuntimeWarning
    else:
        return None

MODEL_MAP = ( # describes all fields in the model
    # title
    {'type': unicode,
     'delegate': None},
    # price
    {'type': float,
     'delegate': QComboBox},
    # paid
    {'type': float,
     'delegate': QLineEdit},
    # paid status
    {'type': lambda x: PAID_STATUS[int(x)],
     'delegate': QComboBox},
    # card type
    {'type': lambda x: CARD_TYPE[int(x)],
     'delegate': QComboBox},
    # count sold
    {'type': int,
     'delegate': None},
    # count used
    {'type': int,
     'delegate': None},
    # duration in days
    {'type': int,
     'delegate': QComboBox},
    # reg_date
    {'type': _dtapply,
     'delegate': None},
    # begin date
    {'type': _dtapply,
     'delegate': None},
    # end date
    {'type': _dtapply,
     'delegate': None},
    # cancel date
    {'type': _dtapply,
     'delegate': None},
    # record id
    {'type': int,
     'delegate': None},
    # team id
    {'type': int,
     'delegate': None},
)

class TeamListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.storage = [] # here the data is stored
        self.hidden_fields = 3 # from end of following lists

        self.labels = [_('Title'), _('Price, rub'), _('Paid, rub'), _('Paid status'),
                       _('Card'), _('Sold'), _('Used'), _('Duration'),
                       _('Assigned'), _('Begin'), _('Expired'), _('Cancelled'),
                       'id', 'team_id', 'price_category']
        self.model_fields = ['title', 'price', 'paid', 'paid_status',
                             'card_type', 'count_sold', 'count_used', 'duration',
                             'reg_datetime', 'begin_date', 'end_date', 'cancel_datetime',
                             'id', 'team_id', 'price_category']

    def initData(self, data, prices):
        """
        Формат полученных данных: см. методы about() у моделей.
        Вызывается из DlgClientInfo::initData()
        """
        self.prices = prices

        for rec in data:
            if type(rec) is not dict:
                raise 'Check format'
            team = rec['team']
            self.storage.append( [
                team['title'],
                rec['price'],
                rec['paid'],
                rec['paid_status'],
                rec['card_type'],
                rec['count_sold'],
                rec['count_used'],
                rec['duration'],
                rec['reg_datetime'],
                rec['begin_date'],
                rec['end_date'],
                rec['cancel_datetime'],
                rec['id'],
                team['id'],
                team['price_category'],
                ] )
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

#         self.emit(SIGNAL('columnsInserted(QModelIndex, int, int)'),
#                   QModelIndex(), 1, cols)
#         self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
#                   self.createIndex(0, 0),
#                   self.createIndex(self.rowCount(), self.columnCount()))

    def get_model_as_formset(self, client_id):
        formset = {
            'form-TOTAL_FORMS': str(len(self.storage)),
            'form-INITIAL_FORMS': u'0',
            }
        for record in self.storage:
            index = self.storage.index(record)

            title, price, paid, paid_status, card_type, \
            count_sold, count_used, duration, \
            reg_datetime, begin_date, exp_date, cancel_datetime, \
            card_id, team_id, price_category = record

            row = {
                'form-%s-client' % index: client_id,
                'form-%s-card' % index: card_id,
                'form-%s-team' % index: team_id,
                'form-%s-price' % index: price,
                'form-%s-paid' % index: paid,
                'form-%s-paid_status' % index: paid_status,
                'form-%s-card_type' % index: card_type,
                'form-%s-count_sold' % index: count_sold,
                'form-%s-duration' % index: duration,
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
            return len(self.model_fields) - self.hidden_fields

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

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole) :
            return QVariant()
        idx_row = index.row()
        idx_col = index.column()
        record = list(self.storage[idx_row])

        object_type = MODEL_MAP[idx_col]['type']
        try:
            value = record[idx_col]
        except IndexError:
            return QVariant() # запись в модели ещё не заполнена

        if value is None:
            return QVariant() # пустое значение
        else:
            return QVariant(object_type(value))

    def setRow(self, index, data, role):
        data_demo = {
            'card_type': 0,
            'duration': 0,
            'team': [u'\u0411\u0440\u0435\u0439\u043a-\u0434\u0430\u043d\u0441 \u0438 free style',
                     1,
                     '0',
                     {'birth_date': '2010-04-30',
                      'desc': u'\u0431\u0443\u0445\u0430\u0435\u0442',
                      'email': 'ivan@jet.ru',
                      'first_name': u'\u0418\u0432\u0430\u043d',
                      'id': 2,
                      'last_name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439',
                      'name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439 \u0418\u0432\u0430\u043d',
                      'phone': '1234567890'},
                     1.0]}

        if index.isValid() and role == Qt.EditRole:
            reg_datetime = datetime.now()
            team_id = data['team'][1]
            title = data['team'][0]
            price = data['team'][2]
            paid = 0
            paid_status = 0
            card_type = data['card_type']
            count_sold = count_used = 0
            duration = data['duration']
            begin_date = exp_date = cancel_datetime = None

            record = [title, price, paid, paid_status, card_type,
                      count_sold, count_used, duration,
                      reg_datetime, begin_date, exp_date, cancel_datetime,
                      0, team_id]

            idx_row = index.row()
            idx_col = 0
            for i in record:
                self.setData(self.createIndex(idx_row, idx_col), i, role)
                idx_col += 1

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = index.column()
            #print '[%i, %i] %s' % (idx_row, idx_col, value)

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

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        print 'TeamListDelegate: constructor'

    def createEditor(self, parent, option, index):
        delegate_editor = MODEL_MAP[ index.column() ]['delegate']
        if delegate_editor:
            print 'return editor', delegate_editor
            return delegate_editor(parent)
        else:
            return None

    def setEditorData(self, editor, index):
        model = index.model()
        raw_value = model.data(index, Qt.DisplayRole)

        delegate_editor = MODEL_MAP[ index.column() ]['delegate']
        if not delegate_editor or delegate_editor is QLineEdit:
            value = raw_value.toString()
            editor.setText(value)
        elif delegate_editor is QComboBox:
            if 1 == index.column(): #price
                idx_price_cat = model.index(index.row(), 14)
                price_cat, ok = model.data(idx_price_cat, Qt.DisplayRole).toInt()
                for i in model.prices:
                    if price_cat == int( i['price_category'] ):
                        cost = unicode( int( float( i['cost'] ) ) )
                        editor.addItem( cost, QVariant(i['id']) )
            elif 3 == index.column(): # paid status
                for i in PAID_STATUS:
                    editor.addItem( i, QVariant(PAID_STATUS.index(i)) )
            elif 4 == index.column(): # card type
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
        delegate_editor = MODEL_MAP[ index.column() ]['delegate']
        if not delegate_editor or delegate_editor is QLineEdit:
            value = editor.text()
        elif delegate_editor is QComboBox:
            if 1 == index.column():
                value = editor.currentText()
            else:
                value = editor.currentIndex()
        elif delegate_editor is QDateEdit:
            value = str(editor.date().toPyDate())
        else:
            value = 'Not implemented'
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
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

        # source model
        self.model_obj = TeamListModel(self)
        self.setModel(self.model_obj)

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
