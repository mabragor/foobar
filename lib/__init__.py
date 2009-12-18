# -*- coding: utf-8 -*-
from django.utils import simplejson

import time
from datetime import datetime

def str2date(value):
    return datetime(*time.strptime(value, '%Y-%m-%d %H:%M:%S')[:6])

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

class DatetimeJSONEncoderQt(simplejson.JSONEncoder):

    def default(self, o):
        from django.utils import datetime_safe
        from datetime import datetime
        import time

        if isinstance(o, datetime):
            d = o.strftime('%Y-%m-%d %H:%M:%S')
            return d
        else:
            return super(DatetimeJSONEncoder, self).default(o)
