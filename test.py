#!/usr/bin/env python

from hashlib import sha1
#from app.data_collect import Extract
from app.models import db_handler


#ext = Extract('2016-01-25', '/Users/kevin/study/python/flask/myproj')
#ext.run_extract()

user_dict = {
        'admin':'admin',
        'kevin':'kevinlee',
        'lwn':'lwn1234',
        'ff':'ff1234',
        'mxc':'mxc1234'}


for k, v in user_dict.items():
    db_handler.save_user(k, sha1(v).hexdigest())

print db_handler.get_user_passwd('admin')
