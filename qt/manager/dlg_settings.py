# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgSettings(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(TabGeneral(), _('General'))
        self.tabWidget.addTab(TabNetwork(), _('Network'))

        self.tabIndex = ['general', 'network']

        applyButton = QPushButton(_('Apply'))
        cancelButton = QPushButton(_('Cancel'))

        self.connect(applyButton, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(cancelButton, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(applyButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle(_('Settings'))

        # load settings
        self.settings = QSettings()
        self.loadSettings()

    def applyDialog(self):
        """ Apply settings. """
        self.saveSettings()
        self.accept()

    def loadSettings(self):
        """ Load settings. """
        for index in xrange(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            tab.loadSettings(self.settings)

    def saveSettings(self):
        """ Save settings. """
        for index in xrange(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            data = tab.saveSettings(self.settings)

class TabAbstract(QWidget):

    def __init__(self, parent=None):
        self.parent = parent

    def saveSettings(self, settings):
        is_changed = False
        settings.beginGroup(self.groupName)
        for name in self.defaults.keys():
            field = getattr(self, name)
            if type(field) is QLineEdit:
                value = field.text()
            elif type(field) is QCheckBox:
                value = field.isChecked()
            original_value = self.defaults[name]
            if original_value != value:
                is_changed = True
            settings.setValue(name, QVariant(value))
        settings.endGroup()
        return is_changed

    def loadSettings(self, settings):
        settings.beginGroup(self.groupName)
        for name in self.defaults.keys():
            field = getattr(self, name)
            raw_value = settings.value(name, QVariant(self.defaults[name]))
            if type(field) is QLineEdit:
                value = raw_value.toString()
                field.setText(value)
            elif type(field) is QCheckBox:
                value = raw_value.toBool()
                field.setChecked(value)
            # keep for compare when saving
            self.defaults[name] = value
        settings.endGroup()

class TabGeneral(TabAbstract):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.groupName = 'general'

        self.defaults = {}

class TabNetwork(TabAbstract):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.groupName = 'network'

        self.defaults = {'addressHttpServer': 'localhost',
                         'portHttpServer': '8000',
                         'useProxy': 'false',
                         'addressHttpProxy': '',
                         'portHttpProxy': '',
                         'loginProxyAuth': '',
                         'passwordProxyAuth': ''
                         }

        # the address and port of HTTP server
        labelHttpServer = QLabel(_('HTTP server (address/port)'))
        self.addressHttpServer = QLineEdit()
        self.portHttpServer = QLineEdit()
        boxHttpServer = QHBoxLayout()
        boxHttpServer.addWidget(labelHttpServer)
        boxHttpServer.addWidget(self.addressHttpServer)
        boxHttpServer.addWidget(self.portHttpServer)

        # checkbox to enabling http proxy usage
        self.useProxy = QCheckBox(_('Use HTTP proxy'))

        # http proxy's parameters
        groupHttpProxy = QGroupBox(_('HTTP proxy settings'))

        labelHttpProxy = QLabel(_('Address and port'))
        self.addressHttpProxy = QLineEdit()
        self.portHttpProxy = QLineEdit()
        boxHttpProxy = QHBoxLayout()
        boxHttpProxy.addWidget(self.addressHttpProxy)
        boxHttpProxy.addWidget(self.portHttpProxy)

        labelProxyAuth = QLabel(_('Login and password'))
        self.loginProxyAuth = QLineEdit()
        self.passwordProxyAuth = QLineEdit()
        boxProxyAuth = QHBoxLayout()
        boxProxyAuth.addWidget(self.loginProxyAuth)
        boxProxyAuth.addWidget(self.passwordProxyAuth)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelHttpProxy, 0, 0)
        groupLayout.addLayout(boxHttpProxy, 0, 1)
        groupLayout.addWidget(labelProxyAuth, 1, 0)
        groupLayout.addLayout(boxProxyAuth, 1, 1)

        groupHttpProxy.setLayout(groupLayout)

        self.connect(self.useProxy, SIGNAL('toggled(bool)'), groupHttpProxy, SLOT('setDisabled(bool)'))

        # ToDo: implement this, is disabled now
        self.useProxy.setCheckState(Qt.Unchecked)
        groupHttpProxy.setDisabled(True)

        # connect all items together
        mainLayout = QVBoxLayout()
        mainLayout.addStretch(1)
        mainLayout.addLayout(boxHttpServer)
        mainLayout.addWidget(self.useProxy)
        mainLayout.addWidget(groupHttpProxy)
        self.setLayout(mainLayout)
