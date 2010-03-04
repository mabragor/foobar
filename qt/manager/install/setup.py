# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='pyqounter-manager',
      version='0.1.0',
      description='Accounting System / Manager',
      author='Ruslan Popov',
      author_email='ruslan.popov@gmail.com',
      maintainer='Ruslan Popov',
      maintainer_email='ruslan.popov@gmail.com',
      url='http://snegiri.dontexist.org/pyqounter',
      packages=['pyqounter-manager'],
      package_dir={'pyqounter-manager': 'src/manager'},
      package_data={'pyqounter-manager': ['locale/ru/LC_MESSAGES/*mo', 'manager.css']}
     )
