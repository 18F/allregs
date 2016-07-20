#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

def fix(filepath):
    f = open(filepath)
    html = f.read()
    # html = html.replace("Built with ❤", 'Built with ❤ by <a href="https://18f.gsa.gov/">18F</a>')
    # html = html.replace("https://github.com/anthonygarvan/allregs", "https://github.com/18F/allregs")
    # html = html.replace("not intended for serious use.</h5", "not intended for serious use.</h5>")
    html = html.replace('/allregs/', '/')
    f.close()
    f = open(filepath, 'w')
    f.write(html)
    f.close()

fix('index.html')

for i, filepath in enumerate([os.path.join(dp, f) for dp, dn, fn
                              in os.walk(os.path.expanduser("html"))
                              for f in fn]):
    fix(filepath)

    if i % 1000 == 0:
        print('processed file %d' % i)
