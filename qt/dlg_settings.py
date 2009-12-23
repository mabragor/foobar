# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgSettings(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(TabGeneral(), self.tr('General'))
        self.tabWidget.addTab(TabNetwork(), self.tr('Network'))

        self.tabIndex = ['general', 'network']

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

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr('Settings'))

        # загрузка настроек
        self.settings = QSettings()
        self.loadSettings()

    def applyDialog(self):
        """ Применить настройки. """
        self.saveSettings()
        self.accept()

    def loadSettings(self):
        """ Загрузка настроек. """
        for index in xrange(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            tab.loadSettings(self.settings)

    def saveSettings(self):
        """ Сохранение настроек. """
        for index in xrange(self.tabWidget.count()):
            tab = self.tabWidget.widget(index)
            data = tab.saveSettings(self.settings)

class TabAbstract(QWidget):

    def __init__(self, parent=None):
        self.parent = parent

    def saveSettings(self, settings):
        settings.beginGroup(self.groupName)
        for name in self.defaults.keys():
            field = getattr(self, name)
            if type(field) is QLineEdit:
                value = field.text()
            elif type(field) is QCheckBox:
                value = field.isChecked()
            settings.setValue(name, QVariant(value))
        settings.endGroup()

    def loadSettings(self, settings):
        settings.beginGroup(self.groupName)
        for name in self.defaults.keys():
            field = getattr(self, name)
            if type(field) is QLineEdit:
                field.setText(settings.value(name, QVariant(self.defaults[name])).toString())
            elif type(field) is QCheckBox:
                field.setChecked(settings.value(name, QVariant(self.defaults[name])).toBool())
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

        # адрес и порт HTTP сервера
        labelHttpServer = QLabel(self.tr('HTTP server (address/port)'))
        self.addressHttpServer = QLineEdit()
        self.portHttpServer = QLineEdit()
        boxHttpServer = QHBoxLayout()
        boxHttpServer.addWidget(labelHttpServer)
        boxHttpServer.addWidget(self.addressHttpServer)
        boxHttpServer.addWidget(self.portHttpServer)

        # галка включения HTTP прокси
        self.useProxy = QCheckBox(self.tr('Use HTTP proxy'))

        # параметры HTTP прокси
        groupHttpProxy = QGroupBox(self.tr('HTTP proxy settings'))

        labelHttpProxy = QLabel(self.tr('Address and port'))
        self.addressHttpProxy = QLineEdit()
        self.portHttpProxy = QLineEdit()
        boxHttpProxy = QHBoxLayout()
        boxHttpProxy.addWidget(self.addressHttpProxy)
        boxHttpProxy.addWidget(self.portHttpProxy)

        labelProxyAuth = QLabel(self.tr('Login and password'))
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

        # сигнал-слот
        self.connect(self.useProxy, SIGNAL('toggled(bool)'), groupHttpProxy, SLOT('setDisabled(bool)'))

        # будующий функционал надо отключать
        self.useProxy.setCheckState(Qt.Unchecked)
        groupHttpProxy.setDisabled(True)

        # подключаем все элементы
        mainLayout = QVBoxLayout()
        mainLayout.addStretch(1)
        mainLayout.addLayout(boxHttpServer)
        mainLayout.addWidget(self.useProxy)
        mainLayout.addWidget(groupHttpProxy)
        self.setLayout(mainLayout)
