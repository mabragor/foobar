# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('statistic.views',
    url(r'^$', 'index', name='index'),
    url(r'^courses/$', 'courses', name='courses'),                   
)