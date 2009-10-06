# -*- coding: utf-8 -*-

from django.http import Http404

def test(request):
    raise Http404
