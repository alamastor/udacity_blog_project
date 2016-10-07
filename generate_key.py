#!/usr/bin/env python

import binascii
import os


key = binascii.hexlify(os.urandom(32)).decode('ascii')
with open('blog/auth.cfg', 'w') as w:
    w.write("[Keys]\nsession = '%s'" % key)
