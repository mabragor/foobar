# -*- coding: utf-8 -*-

from django.http import Http500

def test(request):
    raise Http500
