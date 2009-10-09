# -*- coding: utf-8 -*-
from django.db import connection

def execute_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    keys = [t[0] for t in cursor.description]
    result = [dict(zip(keys,row)) for row in rows]
    return result

