#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from http_ajax import HttpAjax
from tree_model import TreeItem, AbstractTreeModel

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgUserInfo(QDialog):

    def __init__(self, mode, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(800)

        # основные данные пользователя
        labelFirstName = QLabel(self.tr('First name'))
        labelLastName = QLabel(self.tr('Last name'))
        labelEmail = QLabel(self.tr('Email'))
        labelYearBirth = QLabel(self.tr('Year of birth'))
        labelUserSex = QLabel(self.tr('Sex'))

        self.editFirstName = QLineEdit()
        self.editLastName = QLineEdit()
        self.editEmail = QLineEdit()
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
        layoutUser.addWidget(labelEmail, 2, 0)
        layoutUser.addWidget(self.editEmail, 2, 1)
        layoutUser.addWidget(labelYearBirth, 3, 0)
        layoutUser.addWidget(self.editYearBirth, 3, 1)
        layoutUser.addWidget(labelUserSex, 4, 0)
        layoutUser.addWidget(self.editUserSex, 4, 1)

        groupUser = QGroupBox(self.tr('Base data'))
        groupUser.setLayout(layoutUser)

        # купленные курсы
        self.cardinfo = QTableWidget(1, 7)
        labels = [self.tr('Title'), self.tr('Assigned'),
                  self.tr('Used'), self.tr('Price'),
                  self.tr('Bought'), self.tr('Expired'),
                  self.tr('Action')]
        self.cardinfo.setHorizontalHeaderLabels(QStringList(labels))

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(self.tr('Course\'s history'))
        groupCard.setLayout(cardLayout)

#         # курсы, которые можно приобрести
#         self.coursesModel = TreeModel(self.getCourses())
#         courses = CoursesTree(self)
#         courses.setModel(self.coursesModel)

#         courseLayout = QVBoxLayout()
#         courseLayout.addWidget(courses)

#         groupCourses = QGroupBox(self.tr('Available courses'))
#         groupCourses.setLayout(courseLayout)

        assignButton = QPushButton(self.tr('Assign'))
        applyButton = QPushButton(self.tr('Apply'))
        cancelButton = QPushButton(self.tr('Cancel'))

        self.connect(applyButton, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(cancelButton, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(assignButton)
        buttonLayout.addStretch(20)
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(cancelButton)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addWidget(groupCard)
        #layout.addWidget(assignButton)
        #layout.addWidget(groupCourses)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(self.tr('User\'s information'))

    def setData(self, data):
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))

        courses = data.get('course_list', [])
        for record in courses:
            row = self.cardinfo.rowCount()
            self.cardinfo.setRowCount(row+1)

            cancelButton = QPushButton(self.tr('Cancel'))
            self.connect(cancelButton, SIGNAL('clicked()'), self.cancelCourse)

            self.cardinfo.setItem(row-1, 0, QTableWidgetItem(record['title']))
            self.cardinfo.setItem(row-1, 1, QTableWidgetItem(str(record['count_sold'])))
            self.cardinfo.setItem(row-1, 2, QTableWidgetItem(str(record['count_used'])))
            self.cardinfo.setItem(row-1, 3, QTableWidgetItem(str(record['price'])))
            self.cardinfo.setItem(row-1, 4, QTableWidgetItem(record['reg_date']))
            self.cardinfo.setItem(row-1, 5, QTableWidgetItem(record['exp_date']))
            self.cardinfo.setCellWidget(row-1, 6, cancelButton)

    def cancelCourse(self):
        print 'cancel course'
        row = self.cardinfo.currentRow()
        print row
        self.cardinfo.removeRow(row)

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
