# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from datetime import datetime, date, timedelta

from settings import _, DEBUG, userRoles
GET_ID_ROLE = userRoles['getObjectID']

from PyQt4.QtGui import *
from PyQt4.QtCore import *

PAID_STATUS = [_('Reserved'),
               _('Piad partially'),
               _('Paid')]

def date2str(value):
    valtype = type(value)
    if valtype is date:
        return value.strftime('%Y-%m-%d')
    elif valtype is unicode:
        return value
    else:
        raise RuntimeWarning('It must be date but %s' % type(value))

def dt2str(value):
    FORMAT = '%Y-%m-%d %H:%M:%S'
    valtype = type(value)
    if valtype is datetime:
        return value.strftime(FORMAT)
    elif valtype is unicode:
        try:
            datetime.strptime(value, FORMAT)
            return value
        except:
            pass
    raise RuntimeWarning('It must be datetime but %s' % type(value))

MODEL_MAP_RAW = (
    ('card_type', None, _('Type'), str, False),
    ('card_meta', None, _('Meta'), unicode, False),
    ('discount', None, _('Discount'), int, True),
    ('price_category', None, _('Category'), int, True),
    ('price', None, _('Price'), float, False),
    ('paid', None, _('Paid'), float, False),
    ('count_sold', None, _('Sold'), int, False),
    ('count_used', None, _('Used'), int, False),
    ('count_available', None, _('Available'), int, False),
    ('begin_date', None, _('Begin'), date2str, False),
    ('end_date', None, _('End'), date2str, False),
    ('reg_datetime', None, _('Register'), dt2str, False),
    ('cancel_datetime', None, _('Cancel'), dt2str, False),
    ('id', None, 'id', int, False), # of card
)
MODEL_MAP = list()
for name, delegate, title, action, static in MODEL_MAP_RAW:
    record = {'name': name, 'delegate': delegate,
             'title': title, 'action': action}
    MODEL_MAP.append(record)

class CardListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.static = parent.static
        self.storage = [] # here the data is stored, as list of dictionaries
        self.hidden_fields = 1 # from end of following lists

    def initData(self, card_list):
        """
        Data format is described in about() method of models.
        Is called from DlgClientInfo::initData()
        """
        import pprint
        for item in card_list:
            print '======\nITEM\n======'
            pprint.pprint(item)
            self.insert_exist(item, 0)
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

    def dump(self):
        import pprint
        print 'CardListModel dump is'
        pprint.pprint(self.storage)

    def get_model_as_formset(self, client_id):
        """ This method return Django-like formset dictionary using
        the model's description."""
        # Basement
        formset = {
            'form-TOTAL_FORMS': str(len(self.storage)),
            'form-INITIAL_FORMS': u'0',
            }
        # Fill the formset
        for record_index, record in enumerate(self.storage):
            prefix = 'form-%i' % record_index
            row = {'%s-client' % prefix: client_id,}
            for model_index, model_row in enumerate(MODEL_MAP_RAW):
                name, delegate, title, action, static = model_row
                key = '%s-%s' % (prefix, name)
                value = record[model_index]
                value_t = type(value)

                if value is None: # send None as empty string
                    value = str()
                elif value_t is datetime:
                    value = dt2str(value)
                elif value_t is date:
                    value = date2str(value)
                elif value_t in (int, float):
                    value = str(value)
                elif value_t is dict:
                    if 'id' in value:
                        value = value['id']
                    else:
                        value = 'no id found'

                row.update( {key: value} )
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
            return QVariant(section+1) # order number
        return QVariant()

    def flags(self, index): # base class method
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def prepare_proxy(self, slug):
        return lambda card: self.prepare_testonce(card, slug)

    def insert_new(self, card, position, role=Qt.EditRole):
        """ Insert a record into the model. Parameter 'card' has an
        information obtained from UI dialogs."""

        handlers = {
            'flyer': (self.prepare_flyer, 'card_ordinary'),
            'test': (self.prepare_proxy('test'), 'card_ordinary'),
            'once': (self.prepare_proxy('once'), 'card_ordinary'),
            'abonement': (self.prepare_abonement, 'card_ordinary'),
            }
        slug = card['slug']
        handle, card_type = handlers[slug]
        info = handle(card) # here is a dictionary

        card_desc_list = self.static[card_type]
        search_result = filter(lambda a: a['slug'] == slug, card_desc_list)
        if len(search_result) != 1:
            raise Exception('Check card type list')
        this_card = search_result[0]

        record = []

        for name, delegate, title, action, use_static in MODEL_MAP_RAW:
            value = info.get(name, None)
            if use_static:
                if value and name == 'price_category':
                    value = filter(
                        lambda a: a['id'] == value,
                        this_card['price_categories']
                        )[0]
                if value and name == 'discount':
                    value = filter(
                        lambda a: a['id'] == value,
                        self.static['discounts']
                        )[0]
            print '%s = %s' % (name, value)
            record.append(value)
        record.append(0) # this record is not registered in DB yet

        self.storage.insert(0, record)
        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, 1)

    def insert_exist(self, card, position, role=Qt.EditRole):
        #import pprint; pprint.pprint(card)
        """ Insert a record into the model. """
        if card['card_ordinary'] is not None:
            slug = card['card_ordinary']['slug']
            card['card_type'] = slug
        elif card['card_club'] is not None:
            slug = card['card_club']['slug']
            card['card_type'] = 'club'
        elif card['card_promo'] is not None:
            slug = card['card_promo']['slug']
            card['card_type'] = 'promo'
        else:
            raise

        record = []

        for name, delegate, title, action, static in MODEL_MAP_RAW:
            value = card.get(name, None)
            print '%s = %s' % (name, value)
            record.append(value)

        self.storage.insert(0, record)

    def prepare_flyer(self, card):
        return {
            'id': 0,
            'card_type': 'flyer',
            'card_meta': None,
            'discount': 1,
            'price_category': card['price_category'],
            'price': 0,
            'paid': 0,
            'count_sold': 1,
            'count_used': 0,
            'count_available': 1,
            'begin_date': date.today(),
            'end_date': date.today(),
            'reg_datetime': datetime.now(),
            'cancel_datetime': None
            }

    def prepare_testonce(self, card, slug):
        return {
            'id': 0,
            'card_type': slug,
            'card_meta': None,
            'discount': 1,
            'price_category': card['price_category'],
            'price': card['price'],
            'paid': card['paid'],
            'count_sold': card['count_sold'],
            'count_used': 0,
            'count_available': card['count_available'],
            'begin_date': date.today(),
            'end_date': date.today(),
            'reg_datetime': datetime.now(),
            'cancel_datetime': None
            }

    def prepare_abonement(self, card):
        return {
            'id': 0,
            'card_type': 'abonement',
            'card_meta': None,
            'discount': card['discount'],
            'price_category': card['price_category'],
            'price': card['price'],
            'paid': card['paid'],
            'count_sold': card['count_sold'],
            'count_used': 0,
            'count_available': card['count_available'],
            'begin_date': None,
            'end_date': None,
            'reg_datetime': datetime.now(),
            'cancel_datetime': None
            }

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant('error')
        if role not in (Qt.DisplayRole, Qt.ToolTipRole, GET_ID_ROLE) :
            return QVariant()
        idx_row = index.row()
        idx_col = index.column()

        field_obj = MODEL_MAP[idx_col]
        field_name = field_obj['name']
        delegate_editor = field_obj['delegate']
        action = field_obj['action']

        try:
            record = self.storage[idx_row]
            value = record[idx_col]
        except KeyError:
            #import pprint; pprint.pprint(self.storage)
            return QVariant('-err-')
        except IndexError:
            return QVariant('-err-')

        if value is None:
            return QVariant('--')

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

        if type(value) is dict and 'title' in value:
            return QVariant(value['title'])

        return action(value)

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

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            del(self.storage[position + i])
        self.endRemoveRows()
        return True

    def price_matrix(self, card_type, price_cat, count_sold):
       return 42

    def calculate_price(self, index):
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
                # get the card type id
                raw = model.data(model.index(row, 0), GET_ID_ROLE)

                ct_id, ok = raw.toInt()
                # the the list of all cards
                possible_card_types = self.static.get('card_types', [])
                # search information for needed card
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

    """ Courses list. """

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

        #self.delegate = CardListDelegate(self)
        #self.setItemDelegate(self.delegate)

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
