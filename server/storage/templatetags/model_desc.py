# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from django import template
from django.db.models import get_model

register = template.Library()

@register.simple_tag
def model_desc(url, app_name=None):
    values = url.split('/')
    if len(values) > 2: # project mode
        model_name = values[1]
    else: # application mode
        model_name = values[0]
    return getattr(get_model(app_name, model_name), 'description', '')
