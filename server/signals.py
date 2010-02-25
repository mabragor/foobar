# -*- coding: utf-8 -*-
# (c) 2010 Ruslan Popov <ruslan.popov@gmail.com>

from django.dispatch import Signal

signal_log_action = Signal(providing_args=['action'])
