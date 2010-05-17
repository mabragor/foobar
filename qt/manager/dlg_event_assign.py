# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _
from settings import userRoles
from team_tree import TeamTree
from http import Http

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

        row = 0
        groupLayout.addWidget(labelDate, row, 0)
        groupLayout.addWidget(self.editDate, row, 1)
        row += 1
        groupLayout.addWidget(labelTime, row, 0)
        groupLayout.addWidget(self.editTime, row, 1)
        row += 1
        if self.mode == 'rent':
            labelDuration = QLabel(_('Duration'))
            self.editDuration = QTimeEdit()
            labelDuration.setBuddy(self.editDuration)
            self.editDuration.setTime(QTime(1, 0))
            groupLayout.addWidget(labelDuration, row, 0)
            groupLayout.addWidget(self.editDuration, row, 1)
            row += 1

        groupLayout.addWidget(labelRoom, row, 0)
        groupLayout.addWidget(self.comboRoom, row, 1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)

        if self.mode == 'training':
            self.tree = TeamTree(self)
            teamLayout = QVBoxLayout()
            teamLayout.addWidget(self.tree)
            groupTeams = QGroupBox(_('Available teams'))
            groupTeams.setLayout(teamLayout)
            mainLayout.addWidget(groupTeams)

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

            ajax = HttpAjax(self, '/manager/get_rents/', {}, self.parent.session_id)
            response = ajax.parse_json()
            self.rent_list = response['rent_list']
            status_desc = ( _('Reserved'),
                            _('Paid partially'),
                            _('Paid') )
            if len(self.rent_list) == 0:
                self.buttonAssign.setDisabled(True)
            for row in self.rent_list:
                lastRow = self.rent.rowCount()
                self.rent.insertRow(lastRow)

                renter = '%s %s' % (row['renter']['last_name'],
                                    row['renter']['first_name'])
                status = [_('Reserved'), _('Paid partially'), _('Paid')][int( row['status'] )]

                self.rent.setItem(lastRow, 0, QTableWidgetItem(renter))
                self.rent.setItem(lastRow, 1, QTableWidgetItem(status))
                self.rent.setItem(lastRow, 2, QTableWidgetItem(row['title']))
                self.rent.setItem(lastRow, 3, QTableWidgetItem(row['begin_date']))
                self.rent.setItem(lastRow, 4, QTableWidgetItem(row['end_date']))

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
            team = index.data(userRoles['getObjectID']).toPyObject()
            if type(team) is not list:
                return QMessageBox.warning(
                    self,
                    _('Warning'),
                    '\n'.join([_('What team do you want to assign?'),
                               _('Choose the team on the team\'s tree.')]),
                    QMessageBox.Ok, QMessageBox.Ok)
            self.callback(e_date, e_time, room, team)
        else:
            e_duration = self.editDuration.time().toPyTime()
            rent = self.rent_list[ self.rent.currentRow() ]
            self.callback(e_date, e_time, e_duration, room, rent)
        self.accept()
