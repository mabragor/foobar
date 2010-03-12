# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'views.login'),

    url(r'^client/', include('client.urls', namespace='client')),
    url(r'^manager/', include('manager.urls', namespace='manager')),
    url(r'^statistic/', include('statistic.urls', namespace='statistic')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
