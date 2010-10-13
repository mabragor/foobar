# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'manager.views',
#     url(r'^$', 'index'),
#     url(r'^add_event/$', 'ajax_add_event', name='ajax_add_event'),
#     url(r'^add_event/(?P<pk>\d+)/$', 'ajax_add_event'),
#     url(r'^del_event/$', 'ajax_del_event', name='ajax_del_event'),
#     url(r'^change_date/$', 'ajax_change_date', name='ajax_change_date'),
#     url(r'^get_events/$', 'ajax_get_events', name='ajax_get_events'),
#     url(r'^ajax_get_user_teams/$', 'ajax_get_user_teams', name='ajax_get_user_teams'),
#     url(r'^get_team_tree/$', 'ajax_get_team_tree', name='ajax_get_team_tree'),
    url(r'^get_rooms/$', 'ajax_get_rooms', name='ajax_get_rooms'),
#     url(r'^del_user_team/$', 'ajax_del_user_couse', name='ajax_del_user_couse'),
#     url(r'^get_coach_list/$', 'ajax_get_coach_list', name='ajax_get_coach_list'),
#     url(r'^get_unstatus_event/$', 'ajax_get_unstatus_event', name='ajax_get_unstatus_event'),
#     url(r'^save_event_status/$', 'ajax_save_event_status', name='ajax_save_event_status'),
#     url(r'^get_status_timer/$', 'ajax_get_status_timer', name='ajax_get_status_timer'),
#     #url(r'^copy_week/$', 'ajax_copy_week', name='ajax_copy_week'),
#     url(r'^add_user_team/$', 'ajax_add_user_team', name='ajax_add_user_team')
    )

urlpatterns += patterns(
    'manager.ajax',
    url(r'^login/$', 'login'),
    url(r'^static/$', 'static'),
    url(r'^get_client_info/$', 'get_client_info'),
    url(r'^get_renter_info/$', 'get_renter_info'),
    url(r'^get_users_info_by_name/$', 'get_users_info_by_name'),
    url(r'^set_client_info/$', 'set_client_info'),
    url(r'^set_client_card/$', 'set_client_card'),
    url(r'^set_renter_info/$', 'set_renter_info'),
    url(r'^set_renter_card/$', 'set_renter_card'),
    url(r'^get_event_info/$', 'get_event_info'),
    url(r'^get_week/$', 'get_week'),
    url(r'^copy_week/$', 'copy_week'), # REMOVEIT
    url(r'^fill_week/$', 'fill_week'),
    url(r'^cal_event_add/$', 'cal_event_add'),
    url(r'^cal_event_del/$', 'cal_event_del'),
    url(r'^exchange_room/$', 'exchange_room'),
    url(r'^register_visit/$', 'register_visit'),
    url(r'^register_rent/$', 'register_rent'),
    url(r'^register_change/$', 'register_change'), # change coaches for the event
    url(r'^register_fix/$', 'register_fix'),
    url(r'^get_visitors/$', 'get_visitors'),
    url(r'^get_rents/$', 'get_rents'),
#    url(r'^get_coaches/$', 'get_coaches'),
    url(r'^get_accounting/$', 'get_accounting'),
    url(r'^add_resource/$', 'add_resource'),
    url(r'^sub_resource/$', 'sub_resource'),
    )
