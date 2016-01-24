#!/usr/bin/env python

"""
    extract the crash info about the cegui and lua
"""

import os
import sys
import getopt
import re
import datetime
import string
import hashlib
from crashinfo_db import Crash_Info_Model, collect_db_info

# the key word used to find the crash in the log file
# CEGUI::ScriptException: is a little special ,if found in the log file
#                         the fallowing two line man be the info needed
# other key words found in the line is we needed info at most circumanstance
key_words = [r'CEGUI::UnknownObjectException',
        r'CEGUI::AlreadyExistsException',
        r'CEGUI::InvalidRequestException',
        r'CEGUI::ScriptException',
        r'LUA ERROR']


def translator(frm='', to='', delete='', keep=None):
    """
        extrant time: 2016-01-14 ==> 20160114
    """
    if len(to) == 1:
        to = to * len(frm)

    trans = string.maketrans(frm, to)
    if keep is not None:
        allchars = string.maketrans('', '')
        delete = string.translate(allchars, delete)

    def translate(s):
        return s.translate(trans, delete)
    return translate


def getNdaysAgoDate(days):
    d = datetime.datetime.now()
    ndayago = d - datetime.timedelta(days)
    return '%d%02d%2d' % (ndayago.year, ndayago.month, ndayago.day)


def checkMatchit(line):
    for key in key_words:
        rlt = re.search(key, line)
        if rlt:
            flag = 0
            if str(key) == 'CEGUI::ScriptException':
                flag = 1
            elif str(key) == 'LUA ERROR' and len(line[63:]) > 5:
                if not re.search('function refid',line[63:]):
                    flag = 2
                else:
                    break
            return True, flag
    return False, -1


def extrctCrashInfo(fname, db, hash_value):
    if not os.path.isfile(fname):
        print "extrctCrashInfo error: ", fname
        return
    fp = open(fname)

    ret, special = False, 0
    cnt = 0
    temp = []
    lua_temp = []
    for line in fp.readlines():
        if len(str(line)) < 2:
            continue

        if special == 1:
            cnt += 1
            temp.append(line.strip())
            if cnt == 2:
                cnt = 0
                ret, special = False, -1
                s = ''.join(temp)
                hval = str(hashlib.md5(s).hexdigest())
                if hval not in hash_value:
                    hash_value[hval] = 1
                    db.save_info(hval, s, 1, 0)
                else:
                    hash_value[hval] += 1
                    db.update(hval, hash_value[hval])
                temp = []
            continue

        ret, special = checkMatchit(line)
        if ret:
            line_seq = line.split(' ')
            s = ' '.join(line_seq[2:])
            if special == 0:
                hval = hashlib.md5(s).hexdigest()
                if hval not in hash_value:
                    hash_value[hval] = 1
                    db.save_info(hval, s, 1, 0)
                else:
                    hash_value[hval] += 1
                    db.update(hval, hash_value[hval])
            elif special == 1:
                temp.append(s)
            else:
                s = line[63:]
                lua_temp.append(s.strip())
            continue

        if len(lua_temp) > 0:
            ret,special = False, -1
            s = '<br/>'.join(lua_temp)
            hval = hashlib.md5(s).hexdigest()
            if hval not in hash_value:
                hash_value[hval] = 1
                db.save_info(hval, s, 1, 0)
            else:
                hash_value[hval] += 1
                db.update(hval, hash_value[hval])
            lua_temp = []

    fp.close()


def main(dir='', beginDate=''):
    if len(dir) == 0:
        print "Please input the log directory"
        sys.exit(2)
    if not os.path.exists(dir):
        print "Wrong directory: %s" % dir
        sys.exit(2)
    # handle the date to begin
    if type(beginDate) == int:
        beginDate = getNdaysAgoDate(beginDate)
    elif type(beginDate) == str:
        beginDate = beginDate
    else:
        beginDate = getNdaysAgoDate(3)

    # the date filter
    date_filter = translator(delete='-')

    dbobj = Crash_Info_Model(date_filter(beginDate))

    all_hash_val = dbobj.fetch_all_hash()

    for f in os.listdir(dir):
        extrctCrashInfo(''.join([LOG_DIR, '/', f]), dbobj, all_hash_val)

    # write back all the hash value
    for k, v in all_hash_val.items():
        dbobj.save_hash(k, v)

    # store the db name into the all_db_info
    #collect_db_info(dbobj.get_db_name(), beginDate)

    dbobj.close()


def usage(progname):
    helpstr = """
usage: python %s -d [log_dir] -t [20150115] -i [2]
    -d , --directory   : the log files exit directory
    -t , --date        : extract info from the date begin to now
    -i , --ago         : extract info from n days ago to now , only one can use,this or the -t option.
                         defalt option with value 3
    -h , --help        : the help info
"""
    print helpstr % progname


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:t:i:h', ['directory=', 'date=', 'ago='])
    except getopt.GetoptError, err:
        print str(err)
        usage(sys.argv[0])
        sys.exit(2)

    LOG_FILE = ''
    LOG_BEGIN = ''
    LOG_DIR = ''

    for o, v in opts:
        if o in ('-h', '--hel'):
            usage(sys.argv[0])
            sys.exit(1)
        elif o in ('-d', '--directory'):
            if v == '.':
                LOG_DIR = os.path.abspath(os.curdir)
            else:
                LOG_DIR = os.path.abspath(v)
                print LOG_DIR
                if not os.path.isdir(LOG_DIR):
                    print "Wrong directory: %s" % LOG_DIR
                    sys.exit(2)
        elif o in ('-t', '--date'):
            LOG_BEGIN = v
        elif o in ('-i', '--ago'):
            LOG_BEGIN = int(v)
        else:
            usage(sys.argv[0])
            sys.exit(3)

    main(dir=LOG_DIR, beginDate=LOG_BEGIN)
