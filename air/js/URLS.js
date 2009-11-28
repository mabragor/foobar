if (typeof(URLS) == 'undefined') URLS = {};
var root = 'http://127.0.0.1:8000';
URLS.update_url = root+'/static/air/updater/update.xml';

URLS.get_course_tree = root+'/manager/get_course_tree/';
URLS.get_user_courses = root+'/manager/ajax_get_user_courses/';
URLS.add_event = root+'/manager/add_event/';
URLS.del_user_course = root+'/manager/del_user_course/';
URLS.add_user_course = root+'/manager/add_user_course/';
URLS.get_coach_list = root+'/manager/get_coach_list/';
URLS.get_unstatus_event = root+'/manager/get_unstatus_event/';
URLS.save_event_status = root+'/manager/save_event_status/';
URLS.get_status_timer = root+'/manager/get_status_timer/';
URLS.copy_week = root+'/manager/copy_week/';
URLS.del_event = root+'/manager/del_event/';
URLS.change_date = root+'/manager/change_date/';
URLS.get_events = root+'/manager/get_events/';
URLS.get_rooms = root+'/manager/get_rooms/';
URLS.get_user_data = root+'/ajax/rfid/';
