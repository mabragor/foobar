# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from django import template
from django.db.models import get_model
from django.utils.translation import ugettext as _

register = template.Library()

@register.simple_tag
def model_desc(url, app_name=None):
    values = url.split('/')
    if len(values) > 2: # project mode
        model_name = values[1]
    else: # application mode
        model_name = values[0]
    model = get_model(app_name, model_name)
    desc = getattr(model, 'model_desc', '')
    is_slave = getattr(model, 'is_slave', False)
    if is_slave:
        return u'%s<br/><span style="color: gray;">%s</span>' % (_(u'Slave model!'), desc)
    return desc
