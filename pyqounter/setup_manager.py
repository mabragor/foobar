# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='pyqounter-manager',
      version='1.0.0',
      description='Accounting System / Manager',
      author='Ruslan Popov',
      author_email='ruslan.popov@gmail.com',
      maintainer='Ruslan Popov',
      maintainer_email='ruslan.popov@gmail.com',
      url='http://snegiri.dontexist.org/pyqounter',
      packages=['qtrmanager'],
      package_dir={'qtrmanager': 'src/qtrmanager'},
      package_data={'qtrmanager': ['locale/*', 'manager.css']}
     )
