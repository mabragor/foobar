# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from settings import _, DEBUG

from PyQt4.QtGui import *
from PyQt4.QtCore import *

RENT_STATUS = [_('Reserved'), _('Paid partially'),
               _('Paid'), _('Cancelled')]

class RentListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        # here the data is stored
        self.storage = []
        self.hidden_fields = 1

        self.labels = [_('Title'), _('Status'), _('Paid'),
                       _('Begin'), _('Expired'), _('Register'),
                       'id', 'team_id']
        self.model_fields = ['title', 'status', 'paid',
                             'begin_date', 'end_date', 'reg_date',
                             'id']

    def initData(self, renter_id, data):
        """ The format of received data: see about() method of the model. """
        self.renter_id = renter_id
        for rec in data:
            if type(rec) is dict:
                row = []
                for field in self.model_fields:
                    row.append( rec[field] )
                self.storage.append( row )
                self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                          QModelIndex(), 1, self.rowCount())
            else:
                raise 'Check format'

    def get_model_as_formset(self):
        formset = {
            'form-TOTAL_FORMS': str(len(self.storage)),
            'form-INITIAL_FORMS': u'0',
            }
        for record in self.storage:
            index = self.storage.index(record)
            row = {}
            for i in record:
                rec_idx = record.index(i)
                field_name = self.model_fields[rec_idx]
                row.update( {'form-%s-%s' % (index, field_name): i} )
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
            return len(self.labels) - self.hidden_fields

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
        # Look at RentListDelegate! These tuples must be synced.
        map = ( unicode, # title
                lambda x: RENT_STATUS[int(x)], # rent status
                float, # paid
                self._dtapply, # begin_data
                self._dtapply, # end_data
                self._dtapply, # reg_data
                int, # record id
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
            import pprint; pprint.pprint(record)
            return
            #########
            title, team_id, count, price, coach, duration = record
            paid = 0
            record = [title, price, paid, card_type, count, 0,
                      reg_date, bgn_date, exp_date, None, 0, team_id]

            idx_row = index.row()
            idx_col = 0
            # set each field
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

class RentListDelegate(QItemDelegate):

    """ The delegate allow to user to change the model values. """

    # Warning! This tuple describes field value types.
    # Look at TeamList::data method! These tuples must be synced.
    map = ( None, # title
            QComboBox, # rent status
            QLineEdit, # paid
            QDateEdit, # begin_data
            QDateEdit, # end_data
            None, # reg_data
            None, # record id
            )

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)
        print 'RentListDelegate: constructor'

#     def eventFilter(obj, event):
#         print 'event type', event.type()

    def createEditor(self, parent, option, index):
        print 'RentListDelegate: createEditor'
        delegate_editor = self.map[ index.column() ]
        if delegate_editor:
            return delegate_editor(parent)
        else:
            return None

    def setEditorData(self, editor, index):
        print 'RentListDelegate: setEditorData'
        raw_value = index.model().data(index, Qt.DisplayRole)

        delegate_editor = self.map[ index.column() ]
        if not delegate_editor or delegate_editor is QLineEdit:
            value = raw_value.toString()
            editor.setText(value)
        elif delegate_editor is QComboBox:
            for i in RENT_STATUS:
                editor.addItem( i, QVariant(RENT_STATUS.index(i)) )
            value = raw_value.toString()
            item_index = editor.findText(value)
            editor.setCurrentIndex( item_index )
        elif delegate_editor is QDateEdit:
            value = raw_value.toDate()
            editor.setDate(value)
        else:
            return None

    def setModelData(self, editor, model, index):
        print 'RentListDelegate: setModelData'

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
        print 'RentListDelegate: updateEditorGeometry'
        editor.setGeometry(option.rect)

class RentList(QTableView):

    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

        self.actionRentCancel = QAction(_('Cancel rent'), self)
        self.actionRentCancel.setStatusTip(_('Cancel current rent.'))
        self.connect(self.actionRentCancel, SIGNAL('triggered()'), self.rentCancel)

        self.delegate = RentListDelegate()
        self.setItemDelegate(self.delegate)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self.contextRow = index.row()
        menu = QMenu(self)
        menu.addAction(self.actionRentCancel)
        menu.exec_(event.globalPos())

    def rentCancel(self):
        if DEBUG:
            print 'canceled [%i]' % self.contextRow
