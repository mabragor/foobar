# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
import simplejson

def render_to(template, processor=None):
    #if processor and not callable(processor):
    #    raise Exception('Processor is not callable.')
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request, processors=processor))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request, processors=processor))
            return output
        return wrapper
    return renderer



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
