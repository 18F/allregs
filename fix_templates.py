#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

for i, filepath in enumerate([os.path.join(dp, f) for dp, dn, fn
                              in os.walk(os.path.expanduser("html"))
                              for f in fn]):
    f = open(filepath)
    html = f.read()
    # html = html.replace("Built with ❤", 'Built with ❤ by <a href="https://18f.gsa.gov/">18F</a>')
    # html = html.replace("https://github.com/anthonygarvan/allregs", "https://github.com/18F/allregs")
    html = html.replace("not intended for serious use.</h5", "not intended for serious use.</h5>")
    f.close()
    f = open(filepath, 'w')
    f.write(html)
    f.close()
    print('processed file %d' % i)
