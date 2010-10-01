# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from django import template
from django.db.models import get_model

register = template.Library()

@register.simple_tag
def model_desc(url):
    app_name = url.split('/')[0]
    model_name = url.split('/')[1]
    return getattr(get_model(app_name, model_name), 'description', '')
