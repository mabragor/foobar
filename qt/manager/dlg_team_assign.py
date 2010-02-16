# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from settings import userRoles
from team_tree import TeamTree

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgTeamAssign(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labelCardType = QLabel(_('Type of card'))
        self.comboCardType = QComboBox()
        labelCardType.setBuddy(self.comboCardType)
        self.comboCardType.addItem(_('Normal'))
        self.comboCardType.addItem(_('Club'))

        labelBeginning = QLabel(_('Team starts'))
        self.editBeginning = QDateEdit()
        labelBeginning.setBuddy(self.editBeginning)
        current = QDate.currentDate()
        self.editBeginning.setDate(current)
        self.editBeginning.setMinimumDate(current)

        labelFinish = QLabel(_('Team ends after'))
        self.comboDuration = QComboBox()
        labelFinish.setBuddy(self.comboDuration)
        self.comboDuration.addItem(_('3 months'))
        self.comboDuration.addItem(_('6 months'))
        self.comboDuration.addItem(_('9 months'))
        self.comboDuration.addItem(_('12 months'))
        self.comboDuration.setDisabled(True)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelCardType, 0, 0)
        groupLayout.addWidget(self.comboCardType, 0, 1)
        groupLayout.addWidget(labelBeginning, 1, 0)
        groupLayout.addWidget(self.editBeginning, 1, 1)
        groupLayout.addWidget(labelFinish, 2, 0)
        groupLayout.addWidget(self.comboDuration, 2, 1)

        self.tree = TeamTree(self)

        teamLayout = QVBoxLayout()
        teamLayout.addWidget(self.tree)

        groupTeams = QGroupBox(_('Available teams'))
        groupTeams.setLayout(teamLayout)

        self.buttonAssign = QPushButton(_('Assign'))
        self.buttonCancel = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonAssign)
        buttonLayout.addWidget(self.buttonCancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)
        mainLayout.addWidget(groupTeams)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Choose the team'))
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
        self.connect(self.comboCardType, SIGNAL('currentIndexChanged(int)'),
                     self.changeDurationState)

    def changeDurationState(self, index):
        self.comboDuration.setDisabled(index == 0)

    def applyDialog(self):
        card_type = self.comboCardType.currentIndex()
        bgn_date = self.editBeginning.date().toPyDate()
        duration = self.comboDuration.currentIndex()
        index = self.tree.currentIndex()
        team_data = index.data(userRoles['getObjectID']).toPyObject()
        self.callback(card_type, bgn_date, duration, team_data)
        self.accept()
