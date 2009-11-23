#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re

from dlg_course_assign import DlgCourseAssign

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class TreeModel(QAbstractItemModel):

    def __init__(self, data, parent=None):
        QAbstractItemModel.__init__(self, parent)

        rootData = []
        rootData.append(QVariant(self.tr('Courses')))
        self.rootItem = TreeItem(rootData)

        """
        Формат полученных данных:
        [ {id, text, cls='folder', allowDrag, text,
           children: [{id, text, cls='file', leaf, text}, ..]
          }, ...
        ]
        """
        for i in data:
            if i['cls'] == 'folder':
                folder = TreeItem( [i['text']], self.rootItem)
                self.rootItem.appendChild(folder)
                for j in i['children']:
                    child = TreeItem( [j['text']], folder)
                    folder.appendChild(child)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role != Qt.DisplayRole:
            return QVariant()

        item = index.internalPointer()

        return QVariant(item.data(index.column()))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return QVariant()

    def index(self, row, column, parent):
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

class CoursesTree(QTreeView):

    """ Класс дерева курсов. """

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)

        self.setAcceptDrops(False)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.rooms = parent.getRooms().get('rows')

        self.getMime = parent.getMime

        self.connect(self, SIGNAL('doubleClicked(QModelIndex)'),
                     self.doubleClickedSignal)



    def doubleClickedSignal(self, index):
        """ Обработчик двойного клика. Отображаем диалог для размещения курса
        на календаре. """
        print 'CoursesTree::doubleClickedSignal', index
        dialog = DlgCourseAssign(self.rooms)
        dialog.exec_()


    def mousePressEvent(self, event):
        """ Обработчик нажатия кнопки мыши. Отрабатываем здесь DnD. """
        if event.button() == Qt.LeftButton:
            print 'lmb'

            index = self.indexAt(event.pos())
            print index

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

