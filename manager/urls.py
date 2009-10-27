# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^add_event/$', 'ajax_add_event', name='ajax_add_event'),
    url(r'^add_event/(?P<pk>\d+)/$', 'ajax_add_event'),
    url(r'^del_event/$', 'ajax_del_event', name='ajax_del_event'),
    url(r'^change_date/$', 'ajax_change_date', name='ajax_change_date'),
    url(r'^get_events/$', 'ajax_get_events', name='ajax_get_events'),
    url(r'^ajax_get_user_courses/$', 'ajax_get_user_courses', name='ajax_get_user_courses'),
    url(r'^get_course_tree/$', 'ajax_get_course_tree', name='ajax_get_course_tree'),
    url(r'^get_rooms/$', 'ajax_get_rooms', name='ajax_get_rooms'),
    url(r'^del_user_course/$', 'ajax_del_user_couse', name='ajax_del_user_couse'),
    url(r'^get_coach_list/$', 'ajax_get_coach_list', name='ajax_get_coach_list'),
    url(r'^get_unstatus_event/$', 'ajax_get_unstatus_event', name='ajax_get_unstatus_event'),
    url(r'^save_event_status/$', 'ajax_save_event_status', name='ajax_save_event_status'),
    url(r'^get_status_timer/$', 'ajax_get_status_timer', name='ajax_get_status_timer'),
    url(r'^copy_week/$', 'ajax_copy_week', name='ajax_copy_week')
)
