# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re

from settings import _
from tree_model import TreeItem, AbstractTreeModel

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class TreeModel(AbstractTreeModel):

    def __init__(self, data, parent=None):
        AbstractTreeModel.__init__(self, data, parent)

    def setData(self, data):
        # Data format:
        # [ {id, title,
        #    children: [
        #    {'coach': {'birth_date': '2010-04-30',
        #               'desc': u'\u0431\u0443\u0445\u0430\u0435\u0442',
        #               'email': 'ivan@jet.ru',
        #               'first_name': u'\u0418\u0432\u0430\u043d',
        #               'id': 2,
        #               'last_name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439',
        #               'name': u'\u041f\u0435\u0442\u0440\u043e\u043f\u043e\u043b\u044c\u0441\u043a\u0438\u0439 \u0418\u0432\u0430\u043d',
        #               'phone': '1234567890'},
        #     'duration': 1.0,
        #     'groups': u'\u0421\u043e\u0432\u0440\u0435\u043c\u0435\u043d\u043d\u044b\u0435 \u0442\u0430\u043d\u0446\u044b',
        #     'id': 1,
        #     'price_category': '0',
        #     'title': u'\u0411\u0440\u0435\u0439\u043a-\u0434\u0430\u043d\u0441 \u0438 free style'},
        #     ...],
        #    ...},
        # ]
        if not data:
            return
        for i in data:
            if 'children' in i:
                folder = TreeItem( [i['title']], self.rootItem)
                self.rootItem.appendChild(folder)
                for j in i['children']:
                    order = ('title', 'id', 'price_category',
                             'coach', 'duration')
                    itemData = []
                    for param in order:
                        itemData.append( j[param] )
                    child = TreeItem(itemData, folder)
                    folder.appendChild(child)

class TeamTree(QTreeView):

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)

        self.setAcceptDrops(False)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

#         rooms = parent.getRooms()
#         if rooms:
#             self.rooms = rooms.get('rows')
#         else:
#             self.rooms = []

#        self.getMime = parent.getMime

#         self.connect(self, SIGNAL('doubleClicked(QModelIndex)'),
#                      self.doubleClickedSignal)



#     def doubleClickedSignal(self, index):
#         """ Обработчик двойного клика. Отображаем диалог для размещения курса
#         на календаре. """
#         print 'TeamTree::doubleClickedSignal', index
#         dialog = DlgTeamAssign(self.rooms)
#         dialog.exec_()


#     def mousePressEvent(self, event):
#         """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
#         if event.button() == Qt.LeftButton:
#             index = self.indexAt(event.pos())

#             itemData = QByteArray()
#             dataStream = QDataStream(itemData, QIODevice.WriteOnly)
#             dataStream << self.model().data(index, Qt.DisplayRole)
#             mimeData = QMimeData()
#             mimeData.setData(self.getMime('team'), itemData)

#             drag = QDrag(self)
#             drag.setMimeData(mimeData)
#             #drag.setPixmap(pixmap)

#             drop_action = {
#                 0: 'Qt::IgnoreAction',
#                 1: 'Qt::CopyAction',
#                 2: 'Qt::MoveAction',
#                 4: 'Qt::LinkAction',
#                 255: 'Qt::ActionMask',
#                 }

#             res = drag.start(Qt.CopyAction)
#             print 'TeamTree::mousePressEvent', drop_action[res]

#         QTreeView.mousePressEvent(self, event)

