#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from http_ajax import HttpAjax
from tree_model import TreeItem, AbstractTreeModel

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgUserInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent

        # основные данные пользователя
        labelFirstName = QLabel(self.tr('First name'))
        labelLastName = QLabel(self.tr('Last name'))
        labelYearBirth = QLabel(self.tr('Year of birth'))
        labelUserSex = QLabel(self.tr('Sex'))

        self.editFirstName = QLineEdit()
        self.editLastName = QLineEdit()
        self.editYearBirth = QLineEdit()
        self.editUserSex = QComboBox()
        self.editUserSex.addItem(self.tr('Male'))
        self.editUserSex.addItem(self.tr('Female'))

        layoutUser = QGridLayout()
        layoutUser.setColumnStretch(1, 1)
        layoutUser.setColumnMinimumWidth(1, 250)

        layoutUser.addWidget(labelFirstName, 0, 0)
        layoutUser.addWidget(self.editFirstName, 0, 1)
        layoutUser.addWidget(labelLastName, 1, 0)
        layoutUser.addWidget(self.editLastName, 1, 1)
        layoutUser.addWidget(labelYearBirth, 2, 0)
        layoutUser.addWidget(self.editYearBirth, 2, 1)
        layoutUser.addWidget(labelUserSex, 3, 0)
        layoutUser.addWidget(self.editUserSex, 3, 1)

        groupUser = QGroupBox(self.tr('Base data'))
        groupUser.setLayout(layoutUser)

        # купленные курсы
        cardinfo = QTableWidget(1, 6)
        labels = [self.tr('Title'), self.tr('Assigned'),
                  self.tr('Used'), self.tr('Price'),
                  self.tr('Bought'), self.tr('Expired')]
        cardinfo.setHorizontalHeaderLabels(QStringList(labels))

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(cardinfo)

        groupCard = QGroupBox(self.tr('Course\'s history'))
        groupCard.setLayout(cardLayout)

        # курсы, которые можно приобрести
        self.coursesModel = TreeModel(self.getCourses())
        courses = CoursesTree(self)
        courses.setModel(self.coursesModel)

        courseLayout = QVBoxLayout()
        courseLayout.addWidget(courses)

        groupCourses = QGroupBox(self.tr('Available courses'))
        groupCourses.setLayout(courseLayout)

        self.assignButton = QPushButton(self.tr('Assign'))

        applyButton = QPushButton(self.tr('Apply'))
        cancelButton = QPushButton(self.tr('Cancel'))

        self.connect(applyButton, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(cancelButton, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(cancelButton)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addWidget(groupCard)
        layout.addWidget(self.assignButton)
        layout.addWidget(groupCourses)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(self.tr('User\'s information'))

    def applyDialog(self):
        """ Применить настройки. """
        #self.saveSettings()
        self.accept()

    def getCourses(self):
        ajax = HttpAjax(self, '/manager/available_courses/', {})
        if ajax:
            json_like = ajax.parse_json()
        else:
            json_like = None
        return json_like

class CoursesTree(QTreeView):

    """ Класс дерева курсов. """

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)


class TreeModel(AbstractTreeModel):

    def __init__(self, data, parent=None):
        AbstractTreeModel.__init__(self, data, parent)

    def processData(self, data):
        """
        Формат полученных данных:
        [ {id, title,
           children: [{id, count, title, price, coaches, duration}, ..]
           }, ...
        ]
        """
        if not data:
            return
        for i in data:
            if 'children' in i:
                folder = TreeItem( [i['title']], self.rootItem)
                self.rootItem.appendChild(folder)
                for j in i['children']:
                    child = TreeItem( [j['title'], j['coaches'], j['count'], j['price']], folder)
                    folder.appendChild(child)
