# -*- coding: utf-8 -*-
from lib.decorators import render_to, ajax_processor

from client import forms
@render_to('client.html')
def index(request):
    return {
    }

@ajax_processor(forms.ActiveCourses)
def get_active_courses(request, form):
    return {}
