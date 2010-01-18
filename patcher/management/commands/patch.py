# -*- coding: utf-8 -*-

# Команда manage.py для наложения патчей на базу.

from django.db import connection
from django.conf import settings
from django.core.management.base import NoArgsCommand

from patcher.models import Applied

import os, glob

class Command(NoArgsCommand):
    help = 'Applied new patches on database. Use before syncdb command.'

    def handle_noargs(self, **options):
        if os.path.basename(os.path.realpath(os.path.curdir)) != 'foobar':
            print 'Go to project\'s root.'
            return

        indir = os.path.join(os.path.curdir, 'patcher', 'patches')
        patch_list = glob.glob(os.path.join(indir, '*.sql'))
        patch_list.sort()
        for infile in patch_list:
            patch_name = os.path.basename(infile).split('.')[0]
            print 'Patch %s ...' % patch_name,
            try:
                applied_patch = Applied.objects.get(name=patch_name)
                print 'applied already'
            except Applied.DoesNotExist:
                print 'applying now'
                cursor = connection.cursor()
                content = open(infile, 'r').readlines()
                for line in content:
                    sql_line = line.strip()
                    if len(sql_line) > 0:
                        print sql_line
                        cursor.execute(sql_line)
                Applied(name=patch_name).save()
