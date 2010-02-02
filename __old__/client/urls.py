# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('client.views',
    url(r'^$', 'index'),

    url(r'^ajax/active_courses/$', 'get_active_courses', name='get_active_courses'),

)

