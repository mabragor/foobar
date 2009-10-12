# -*- coding: utf-8 -*-
from lib.decorators import render_to

@render_to('manager.html')
def index(request):

    return {
    }

