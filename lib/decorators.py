# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _
from lib import DatetimeJSONEncoder

def render_to(template, processor=None):
    def renderer(func):
        def wrapper(request, *args, **kw):
            if processor is not None:
                ctx_proc = RequestContext(request, processors=[processor])
            else:
                ctx_proc = RequestContext(request)
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], ctx_proc)
            elif isinstance(output, dict):
                return render_to_response(template, output, ctx_proc)
            return output
        return wrapper
    return renderer

def ajax_processor(form_object=None):
    def processor(func):
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                if form_object is not None:
                    form = form_object(request.POST)
                    if form.is_valid():
                        result = func(request, form, *args, **kwargs)
                    else:
                        if settings.DEBUG:
                            result = {'code': '301', 'desc': _(u'Form is not valid : %s') % form.errors}
                        else:
                            result = {'code': '301', 'desc': _(u'Service is temporary unavailable. We appologize for any inconvinience.')}
                else:
                    result = func(request, *args, **kwargs)
            else:
                if settings.DEBUG:
                    result = {'code': '401', 'desc': _(u'It must be POST')}
                else:
                    result = {'code': '401', 'desc': _(u'Please, do not break our code :)')}
            json = simplejson.dumps(result, cls=DatetimeJSONEncoder)
            return HttpResponse(json, mimetype="application/json")
        return wrapper
    return processor
