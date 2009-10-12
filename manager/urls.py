# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^add_event/$', 'ajax_add_event', name='ajax_add_event'),
    url(r'^add_event/(?P<pk>\d+)/$', 'ajax_add_event'),
    url(r'^del_event/$', 'ajax_del_event', name='ajax_del_event'),
    url(r'^change_date/$', 'ajax_change_date', name='ajax_change_date'),
    url(r'^get_events/$', 'ajax_get_events', name='ajax_get_events'),
    url(r'^get_course_tree/$', 'ajax_get_course_tree', name='ajax_get_course_tree')
)
