# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import userRoles
from courses_tree import CoursesTree
from http_ajax import HttpAjax

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgEventAssign(QDialog):

    def __init__(self, mode='training', parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.mode = mode
        self.setMinimumWidth(600)

        labelDate = QLabel(_('Date'))
        self.editDate = QDateEdit()
        labelDate.setBuddy(self.editDate)
        current = QDate.currentDate()
        self.editDate.setDate(current)
        self.editDate.setMinimumDate(current)

        labelTime = QLabel(_('Time'))
        self.editTime = QTimeEdit()
        labelTime.setBuddy(self.editTime)
        current = QTime.currentTime()
        time = QTime(current.hour(), current.minute())
        self.editTime.setTime(time)

        labelRoom = QLabel(_('Room'))
        self.comboRoom = QComboBox()
        labelRoom.setBuddy(self.comboRoom)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelDate, 0, 0)
        groupLayout.addWidget(self.editDate, 0, 1)
        groupLayout.addWidget(labelTime, 1, 0)
        groupLayout.addWidget(self.editTime, 1, 1)
        groupLayout.addWidget(labelRoom, 2, 0)
        groupLayout.addWidget(self.comboRoom, 2, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)

        if self.mode == 'training':
            self.tree = CoursesTree(self)
            courseLayout = QVBoxLayout()
            courseLayout.addWidget(self.tree)
            groupCourses = QGroupBox(_('Available courses'))
            groupCourses.setLayout(courseLayout)
            mainLayout.addWidget(groupCourses)

        self.buttonAssign = QPushButton(_('Assign'))
        self.buttonCancel = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonAssign)
        buttonLayout.addWidget(self.buttonCancel)

        if self.mode == 'rent':
            labels = QStringList([_('Renter'), _('Status'), _('Title'),
                                  _('Begin'), _('End')])

            self.rent = QTableWidget(0, 5)
            self.rent.setHorizontalHeaderLabels(labels)
            rentLayout = QVBoxLayout()
            rentLayout.addWidget(self.rent)
            rentGroup = QGroupBox(_('Rents'))
            rentGroup.setLayout(rentLayout)
            mainLayout.addWidget(rentGroup)

            ajax = HttpAjax(self, '/manager/get_rents/', {})
            response = ajax.parse_json()
            self.rent_list = response['rent_list']
            status_desc = ( _('Reserved'),
                            _('Paid partially'),
                            _('Paid') )
            for rent_id, renter, status, title, desc, begin_date, end_date in self.rent_list:
                lastRow = self.rent.rowCount()
                self.rent.insertRow(lastRow)
                self.rent.setItem(lastRow, 0, QTableWidgetItem(renter))
                self.rent.setItem(lastRow, 1, QTableWidgetItem(status_desc[int(status)]))
                self.rent.setItem(lastRow, 2, QTableWidgetItem(title))
                self.rent.setItem(lastRow, 3, QTableWidgetItem(begin_date))
                self.rent.setItem(lastRow, 4, QTableWidgetItem(end_date))
            else:
                print 'Check response format!'

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Assign the event'))
        self.setSignals()

    def setCallback(self, callback):
        self.callback = callback

    def setModel(self, model):
        self.tree.setModel(model)

    def setSignals(self):
        self.connect(self.buttonAssign, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def setRooms(self, rooms):
        for title, color, id in rooms:
            self.comboRoom.addItem(title, QVariant(id))

    def applyDialog(self):
        e_date = self.editDate.date().toPyDate()
        e_time = self.editTime.time().toPyTime()
        index = self.comboRoom.currentIndex()
        room = self.comboRoom.itemData(index).toInt()
        if self.mode == 'training':
            index = self.tree.currentIndex()
            course = index.data(userRoles['getObjectID']).toPyObject()
            if type(course) is not list:
                return QMessageBox.warning(
                    self,
                    _('Warning'),
                    '\n'.join([_('What course do you want to assign?'),
                               _('Choose the course on the course\'s tree.')]),
                    QMessageBox.Ok, QMessageBox.Ok)
            self.callback(e_date, e_time, room, course)
        else:
            rent = self.rent_list[ self.rent.currentRow() ]
            self.callback(e_date, e_time, room, rent)
        self.accept()
