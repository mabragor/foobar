# -*- coding: utf-8 -*-
from django.utils import simplejson

class DatetimeJSONEncoder(simplejson.JSONEncoder):

    class DateInt(int):
        def __str__(self):
            return 'new Date(%s)' % (self*1000)
        
    def default(self, o):
        from django.utils import datetime_safe
        from datetime import datetime
        import time

        if isinstance(o, datetime):
            d = datetime_safe.new_datetime(o)
            return self.DateInt(int(time.mktime(d.timetuple())))
        else:
            return super(DatetimeJSONEncoder, self).default(o)