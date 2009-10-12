# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('rfid.views',
    url(r'^$', 'info_by_rfid'),
)

