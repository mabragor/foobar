# -*- coding: utf-8 -*-

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEFAULT_CHARSET = 'UTF-8'

DATABASE_ENGINE = 'mysql'
DATABASE_PORT = ''

SITE_ID = 1
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru'
USE_I18N = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.webdesign',
    'client',
)

# robots begin
ROBOTS_USE_SITEMAP = True
ROBOTS_SITEMAP_URL = '/sitemap.xml'
# robots end

#calendar
CALENDAR_OPTIONS = {
    'timeslotsPerHour': 2,
    'businessHours' :{
        'start': 8,
        'end': 18,
        'limitDisplay': True
    },
    'timeslotHeight': 30
}

try:
    from settings_local import *
except ImportError:
    pass
