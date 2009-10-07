# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('client.views',
    (r'^$', 'index'),
    url(r'^add_event/$', 'ajax_add_event', name='ajax_add_event'),
    (r'^add_event/(?P<pk>\d+)/$', 'ajax_add_event'),
    url(r'^del_event/$', 'ajax_del_event', name='ajax_del_event'),
    url(r'^change_date/$', 'ajax_change_date', name='ajax_change_date')
)