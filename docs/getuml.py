#!/usr/bin/env python

import urllib
import re
from sys import argv, exit

try:
    source, destination, style = argv[1:]
except:
    print 'Usage: %s <IN> <OUT> <STYLE>' % argv[0]
    print 'Styles are default, earth, modern-blue, mscgen,'
    print '           omegapple, qsd, rose, roundgreen, napkin'
    exit(1)

def getSequenceDiagram( text, outputFile, style = 'default' ):
    print 'Parsing %s using %s style.' % (source, style)
    request = {}
    request["message"] = text
    request["style"] = style

    url = urllib.urlencode(request)

    f = urllib.urlopen("http://www.websequencediagrams.com/", url)
    line = f.readline()
    f.close()

    expr = re.compile("(\?img=[a-zA-Z0-9]+)")
    m = expr.search(line)

    if m == None:
        print "Invalid response from server."
        return False

    urllib.urlretrieve("http://www.websequencediagrams.com/" + m.group(0),
            outputFile )
    return True

text = open(source, 'r').read()

getSequenceDiagram( text, destination, style )

exit(0)
