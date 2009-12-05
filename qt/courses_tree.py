#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re

#from dlg_course_assign import DlgCourseAssign
from tree_model import TreeItem, AbstractTreeModel

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class TreeModel(AbstractTreeModel):

    def __init__(self, data, parent=None):
        AbstractTreeModel.__init__(self, data, parent)

    def processData(self, data):
        """
        Формат полученных данных:
        [ {id, text, cls='folder', allowDrag, text,
           children: [{id, text, cls='file', leaf, text}, ..]
          }, ...
        ]
        """
        if not data:
            return
        for i in data:
            if i['cls'] == 'folder':
                folder = TreeItem( [i['text']], self.rootItem)
                self.rootItem.appendChild(folder)
                for j in i['children']:
                    child = TreeItem( [j['text']], folder)
                    folder.appendChild(child)


class CoursesTree(QTreeView):

    """ Класс дерева курсов. """

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)

        self.setAcceptDrops(False)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        rooms = parent.getRooms()
        if rooms:
            self.rooms = rooms.get('rows')
        else:
            self.rooms = []

        self.getMime = parent.getMime

#         self.connect(self, SIGNAL('doubleClicked(QModelIndex)'),
#                      self.doubleClickedSignal)



#     def doubleClickedSignal(self, index):
#         """ Обработчик двойного клика. Отображаем диалог для размещения курса
#         на календаре. """
#         print 'CoursesTree::doubleClickedSignal', index
#         dialog = DlgCourseAssign(self.rooms)
#         dialog.exec_()


    def mousePressEvent(self, event):
        """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << self.model().data(index, Qt.DisplayRole)
            mimeData = QMimeData()
            mimeData.setData(self.getMime('course'), itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            #drag.setPixmap(pixmap)

            drop_action = {
                0: 'Qt::IgnoreAction',
                1: 'Qt::CopyAction',
                2: 'Qt::MoveAction',
                4: 'Qt::LinkAction',
                255: 'Qt::ActionMask',
                }

            res = drag.start(Qt.CopyAction)
            print 'CoursesTree::mousePressEvent', drop_action[res]

        QTreeView.mousePressEvent(self, event)

