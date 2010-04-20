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
    # rent status
    {'type': lambda x: RENT_STATUS[int(x)],
     'delegate': QComboBox},
    # paid
    {'type': float,
     'delegate': QLineEdit},
    # begin_data
    {'type': _dtapply,
     'delegate': QDateEdit},
    # end_data
    {'type': _dtapply,
     'delegate': QDateEdit},
    # reg_data
    {'type': _dtapply,
     'delegate': None},
    # record id
    {'type': int,
     'delegate': None},
    # desc
    {'type': unicode,
     'delegate': None}
    )

class RentListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.storage = [] # here the data is stored
        self.hidden_fields = 2 # from end of following lists

        self.labels = [_('Title'), _('Status'), _('Paid'),
                       _('Begin'), _('Expired'), _('Assigned'),
                       'id', 'desc']
        self.model_fields = ['title', 'status', 'paid',
                             'begin_date', 'end_date', 'reg_date',
                             'id', 'desc']

    def initData(self, renter_id, data):
        """ The format of received data: see about() method of the model. """
        self.renter_id = renter_id
        for rec in data:
            if type(rec) is dict:
                self.storage.append( [ rec[field] for field in self.model_fields] )
            else:
                raise 'Check format'

        # this signal must be emitted after initializing the model
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

    def get_model_as_formset(self):
        formset = {
            'form-TOTAL_FORMS': str(len(self.storage)),
            'form-INITIAL_FORMS': u'0',
            }

        for record in self.storage:
            index = self.storage.index(record)
            row = {}
            for field_name in self.model_fields:
                rec_idx = self.model_fields.index(field_name)
                value = record[rec_idx]

                # unicode objects have to be converted into utf-8
                if unicode == MODEL_MAP[rec_idx]['type']:
                    if type(value) is QString:
                        value = value.toUtf8()
                    else:
                        value = value.encode('utf-8')

                row.update( {'form-%s-%s' % (index, field_name): value} )
            formset.update( row )
        return formset

    def rowCount(self, parent=None): # base class method
        if parent and parent.isValid():
            return 0
        else:
            return len(self.storage)

    def columnCount(self, parent=None): # base class method
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

    def setRow(self, index, record, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = 0
            # set each field
            for i in self.model_fields:
                self.setData(self.createIndex(idx_row, idx_col), record[i], role)
                idx_col += 1

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = index.column()

            record = list(self.storage[idx_row])
            if len(record) == 0: # init record in this case
                for i in xrange(self.modelColumnCount()):
                    record.append(None)

            # FIXME: I guess no convert is needed.
            if type(value) is QVariant:
                v = value.toString()
            else:
                v = value

            record[idx_col] = v
            self.storage[idx_row] = list(record)
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

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        delegate_editor = MODEL_MAP[ index.column() ]['delegate']

        if delegate_editor:
            return delegate_editor(parent)
        else:
            return None

    def setEditorData(self, editor, index):
        raw_value = index.model().data(index, Qt.DisplayRole)

        delegate_editor = MODEL_MAP[ index.column() ]['delegate']

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
        delegate_editor = MODEL_MAP[ index.column() ]['delegate']

        if not delegate_editor or delegate_editor is QLineEdit:
            value = editor.text()
        elif delegate_editor is QComboBox:
            value = editor.currentIndex()
        elif delegate_editor is QDateEdit:
            value = str(editor.date().toPyDate())
            #print 'delegate setModelData', value, type(value)
        else:
            value = 'Not implemented'
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
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
