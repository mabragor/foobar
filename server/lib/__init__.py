# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>
# (c) 2009      Dmitry <alerion.um@gmail.com>

from django.utils import simplejson, datetime_safe

import time
from datetime import datetime, date

def str2date(value):
    return datetime(*time.strptime(value, '%Y-%m-%d %H:%M:%S')[:6])

class DatetimeJSONEncoder(simplejson.JSONEncoder):

    class DateInt(int):
        def __str__(self):
            return 'new Date(%s)' % (self*1000)

    def default(self, o):

        if isinstance(o, datetime):
            d = datetime_safe.new_datetime(o)
            return self.DateInt(int(time.mktime(d.timetuple())))
        else:
            return super(DatetimeJSONEncoder, self).default(o)

class DatetimeJSONEncoderQt(simplejson.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            d = o.strftime('%Y-%m-%d %H:%M:%S')
            return d
        elif isinstance(o, date):
            d = o.strftime('%Y-%m-%d')
            return d
        else:
            return super(DatetimeJSONEncoder, self).default(o)
