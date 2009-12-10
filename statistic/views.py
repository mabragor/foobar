# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from lib.decorators import render_to
from storage.models import Course

@render_to("statistic/index.html")
@staff_member_required
def index(request):
    return {}

@render_to("statistic/courses.html")
@staff_member_required
def courses(request):
    
    return {
        'items': Course.objects.all()    
    }