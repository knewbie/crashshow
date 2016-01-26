#!/usr/bin/env python

from app.data_collect import Extract

ext = Extract('2016-01-25', '/Users/kevin/study/python/flask/myproj')
ext.run_extract()

print "Over"
