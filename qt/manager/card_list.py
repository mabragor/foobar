# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from settings import _, DEBUG, userRoles
GET_ID_ROLE = userRoles['getObjectID']

from PyQt4.QtGui import *
from PyQt4.QtCore import *

PAID_STATUS = [_('Reserved'),
               _('Piad partially'),
               _('Paid')]

MODEL_MAP_RAW = (
    ('card_types', QComboBox, _('Type of card'), 'complex'),
    ('price_cats_team', QComboBox, _('Price category'), 'id2title'),
    ('count_sold', QComboBox, _('Sold'), 'int'),
    ('price', None, _('Price'), 'float'),
    ('discount', QComboBox, _('Discount'), 'id2title'),
    ('count_available', None, _('Available'), 'int'),
    ('count_used', None, _('Used'), 'int'),
    ('begin date', None, _('Begin'), 'date2str'),
    ('end date', None, _('End'), 'date2str'),
    ('reg datetime', None, _('Register'), 'dt2str'),
    ('cancel datetime', None, _('Cancel'), 'dt2str'),
    ('id', None, 'id', 'int')
)
MODEL_MAP = list()
for name, delegate, title, action in MODEL_MAP_RAW:
    record = {'name': name, 'delegate': delegate,
             'title': title, 'action': action}
    MODEL_MAP.append(record)

class CardListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.static = parent.static
        self.storage = [] # here the data is stored
        self.hidden_fields = 1 # from end of following lists

    def initData(self, card_list):
        """
        Формат полученных данных: см. методы about() у моделей.
        Вызывается из DlgClientInfo::initData()
        """
        self.storage = card_list
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

    def dump(self):
        import pprint
        print 'CardListModel dump is'
        pprint.pprint(self.storage)

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
                'form-%s-price_category' % index: int(price_category), #FIXME
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
            return len(MODEL_MAP) - self.hidden_fields

    def headerData(self, section, orientation, role): # base class method
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(MODEL_MAP[section].get('title', '--'))
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section+1) # порядковый номер
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def converter(self, value, action):
        if value is None:
            return QVariant()

        if action == 'id2title':
            pass
        elif action == 'int':
            return int(value)
        elif action == 'float':
            return float(value)
        elif action == 'date2str':
            return datetime.strptime(value, '%Y-%m-%d').date()
        elif action == 'date2str':
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            raise RuntimeWarning

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole, GET_ID_ROLE) :
            return QVariant()
        idx_row = index.row()
        idx_col = index.column()

        field_obj = MODEL_MAP[idx_col]
        field_name = field_obj['name']
        delegate_editor = field_obj['delegate']
        action = field_obj['action']

        return QVariant() # REMOVE

        try:
            record = self.storage[idx_row]
            value = record[idx_col]
        except IndexError:
            return QVariant()

        if value is None:
            return QVariant()

        if delegate_editor is QComboBox:
            if role == GET_ID_ROLE or action == 'int':
               return QVariant(value)

            # or return title
            items = self.static.get(field_name, list())
            data = filter(lambda x: int(x['id']) == int(value), items)
            if len(data) != 1:
               return QVariant(_('Choose'))
            else:
               value = data[0]['title']
               return QVariant(value)

        return QVariant(self.converter(value, action))

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = index.column()
            field = MODEL_MAP[idx_col]['name']

            record = self.storage[idx_row]
            record[idx_col] = value
            self.storage[idx_row] = record

            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(QModelIndex(), position, len(rows)-1)
        for row in rows:
            column = 0
            record = []

            for name, delegate, title, action in MODEL_MAP_RAW:
                value = row.get(name, None)
                record.append(value)

            self.storage.insert(0, record)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            del(self.storage[position + i])
        self.endRemoveRows()
        return True

    def price_matrix(self, card_type, price_cat, count_sold):
       return 42

    def calculate_price(self, index):
        """ Метод для подсчёта цены по известным типу карты, ценовой
        категории и количеству занятий."""
        row = index.row()
        record = self.storage[row]
        card_type_id = record[0]
        price_cat_id = record[1]
        count_sold   = record[2]
        record[3] = self.price_matrix(card_type_id, price_cat_id, count_sold)
        self.storage[row] = record

        changed = QModelIndex(row, 3)
        self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                  changed, changed)

class CardListDelegate(QItemDelegate):

    """ The delegate allow to user to change the model values. """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

        self.static = parent.static

        self.COUNT_USED_INDEX = self.search('count_used')
        self.PRICE_CAT_INDEX = self.search('price_cats_team')

    def search(self, name):
        result_list = filter(
            lambda x: x['name'] == name, MODEL_MAP
            )
        if len(result_list) != 1:
            raise Exception('Wrong search')
        value = result_list[0]
        return MODEL_MAP.index(value)

    def search_and_get(self, where, field_name, value):
        result_list = filter(
            lambda x: x[field_name] == value, where
            )
        if len(result_list) != 1:
            raise Exception('Wrong search')
        return result_list[0]

    def createEditor(self, parent, option, index):
        delegate_editor = MODEL_MAP[ index.column() ]['delegate']

        # get the state of used trainings
        model = index.model()
        idx_count_used = model.index(index.row(), self.COUNT_USED_INDEX)
        count_used, ok = model.data(idx_count_used, Qt.DisplayRole).toInt()

        # if the card is already used, deny to edit its price
        if 1 == index.column() and 0 < count_used:
            delegate_editor = None

        if delegate_editor:
            return delegate_editor(parent)
        return None

    def setEditorData(self, editor, index):
        model = index.model()
        row = index.row()
        column = index.column()
        raw_value = model.data(index, Qt.DisplayRole)

        field_obj = MODEL_MAP[ column ]
        field_name = field_obj['name']
        delegate_editor = field_obj['delegate']

        if not delegate_editor or delegate_editor is QLineEdit:
            value = raw_value.toString()
            editor.setText(value)
        elif delegate_editor is QDateEdit:
            value = raw_value.toDate()
            editor.setDate(value)
        elif delegate_editor is QComboBox:
            match_list = None
            items = self.static.get(field_name, list())

            if 1 == column:
                # получаем идентификатор типа карты
                raw = model.data(model.index(row, 0), GET_ID_ROLE)
                ct_id, ok = raw.toInt()
                # получаем список всех типов карт
                possible_card_types = self.static.get('card_types', [])
                # находим информацию о нужной
                card_type = self.search_and_get(possible_card_types, 'id', ct_id)
                price_cats = card_type.get('price_categories', [])
                match_list = [i['id'] for i in price_cats]
            if 2 == column:
                possible_values = [1,4]
                v = 8; base = 8; mul = 1
                while v < 366:
                   possible_values.append(v)
                   mul += 1
                   v = base * mul
                items = []
                for i in possible_values:
                   items.append( {'id': i, 'title': str(i)} )

            for i in items:
                if not match_list or i['id'] in match_list:
                    editor.addItem( i['title'], QVariant(i['id']) )

#             if 1 == column:
#                 # get the price category of this card
#                 idx_price_cat = model.index(index.row(), self.PRICE_CAT_INDEX)
#                 price_cat, ok = model.data(idx_price_cat, Qt.DisplayRole).toInt()
#                 for i in model.prices:
#                     if price_cat == int( i['price_category'] ):
#                         cost = unicode( int( float( i['cost'] ) ) )
#                         editor.addItem( cost, QVariant(i['id']) )
#             elif 3 == column: # paid status
#                 for i in PAID_STATUS:
#                     editor.addItem( i, QVariant(PAID_STATUS.index(i)) )
#             elif 4 == column: # card type
#                 for i in CARD_TYPE:
#                     editor.addItem( i, QVariant(CARD_TYPE.index(i)) )
#             elif 7 == column: # duration
#                 for i in DURATION_TYPE:
#                     editor.addItem( str(i), QVariant(DURATION_TYPE.index(i)) )
            value = raw_value.toString()
            item_index = editor.findText(value)
            editor.setCurrentIndex( item_index )
        else:
            return None

    def setModelData(self, editor, model, index):
        column = index.column()

        def generator_price(field_name, value):
            return lambda x: int( value ) == int( x[field_name] )

        delegate_editor = MODEL_MAP[ index.column() ]['delegate']
        if not delegate_editor or delegate_editor is QLineEdit:
            value = editor.text()
        elif delegate_editor is QComboBox:
            idx = editor.currentIndex()
            value, ok = editor.itemData(idx).toInt()
            print value, ok
            #if 1 == index.column():
            #    value = editor.currentText()
                # fill count_sold
                #g = generator_price('cost', value)
                #price_info = filter(g, model.prices)[0]
                #model.setData(model.index(index.row(), 5), price_info['count'], Qt.EditRole)
            #else:
        elif delegate_editor is QDateEdit:
            value = str(editor.date().toPyDate())
        else:
            value = 'Not implemented'

        model.setData(index, value, Qt.EditRole)
        model.dump()

        model.calculate_price(index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class CardList(QTableView):

    """ Класс списка курсов. """

    def __init__(self, parent=None, params=dict()):
        QTableView.__init__(self, parent)

        self.static = params.get('static', None)

        self.verticalHeader().setResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        #self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        #self.resizeColumnsToContents()

        self.actionCardCancel = QAction(_('Cancel card'), self)
        self.actionCardCancel.setStatusTip(_('Cancel current card.'))
        self.connect(self.actionCardCancel, SIGNAL('triggered()'), self.cardCancel)

        # source model
        self.model_obj = CardListModel(self)
        self.setModel(self.model_obj)

        self.delegate = CardListDelegate(self)
        self.setItemDelegate(self.delegate)

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             index = self.indexAt(event.pos())
#             print index.row()

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self.contextRow = index.row()
        menu = QMenu(self)
        menu.addAction(self.actionCardCancel)
        menu.exec_(event.globalPos())

    def cardCancel(self):
        if DEBUG:
            print 'canceled [%i]' % self.contextRow
