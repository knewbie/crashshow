import os
import time
from shutil import copyfile, rmtree
from datetime import datetime, timedelta
from db_utils import DB_model
from data_collect import Extract
from config import DATA_SRC_ROOT, DATA_DEST_ROOT


def time_str_to_int(t=''):
    '''
    the time string must with the format "2016-01-18"
    '''
    return time.mktime(time.strptime(t, "%Y-%m-%d"))


def time_int_to_str(t=0):
    '''
    transform the timestamp to time string
    '''
    return time.strftime("%Y-%m-%d", time.localtime(t))


def db_update_time_to_str(timestamp):
    '''translate the db update time to string '''
    if timestamp is None:
        return ''
    time = datetime.fromtimestamp(timestamp)
    return '%s-%02d-%02d %02d:%02d:%02d' %(time.year,time.month,time.day,time.hour,time.minute,time.second)


def get_ndays_ago_or_after(days=0):
    ''' get the time stamp without ndays
        return datetime.datetime struct
    '''
    return datetime.now() - timedelta(days)


def translator(frm='', to='', delete='', keep=None):
    """
        extrant time: 2016-01-14 ==> 20160114
    """
    if len(to) == 1:
        to = to * len(frm)
    import string
    trans = string.maketrans(frm, to)
    if keep is not None:
        allchars = string.maketrans('', '')
        delete = string.translate(allchars, delete)

    def translate(s):
        return s.translate(trans, delete)
    return translate


def get_db_inst_of_day(date):
    '''
    get the date of the dbname, because our datebase created
    based the date.
    '''
    return DB_model(date)


def get_today_date():
    ''' get today'date with format: 1990-01-01 '''
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def check_today_db():
    '''check if today's db existed'''
    db = './db/' + get_today_date() + '.db'
    if not os.path.isfile(db):
        return False
    return True


def update_today_db():
    ''' update the datebase info '''
    today = get_today_date()
    collect_today_data()
    ext = Extract(today, DATA_DEST_ROOT)
    ext.run_extract()
    return True


def check_upadte_elapse(ts):
    ''' check if can update with 2 hours elapse
        if cross day, that will not allowed to
        update even the elapse is over 2 hours.
        In this situation ,it should be check
        in next day
        return value:   0 => can't update
                        1 => can update
                        2 => cross day
    '''
    now = datetime.now()
    pre = None
    if ts:
        pre = datetime.fromtimestamp(ts)
    else:
        pre = datetime.now()
    dif = datetime(1970, 1, 1) + (now - pre)
    if now.day != pre.day:
        return 2,
    elif dif.hour > 2:
        return 1,
    else:
        return 0, '%s-%02d-%02d %02d:%02d:%02d' %(pre.year,pre.month,pre.day,pre.hour,pre.minute,pre.second)


def collect_today_data():
    from shutil import copyfile
    data_path = os.path.join(DATA_DEST_ROOT, get_today_date())
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    src_dir = os.path.join(DATA_SRC_ROOT, get_today_date())
    if not os.path.exists(src_dir):
        raise ValueError("directory(%s) doesn't existed" % src_dir)
    files = os.listdir(data_path)
    for k in os.listdir(src_dir):
        if 'kof97' in k and k not in files:
            f = ''.join([src_dir, '/', k, '/', 'ledo_game.log'])
            if os.path.isfile(f):
                copyfile(f, ''.join([data_path, '/', k, '_ledo_game.log']))


def collect_history_data():
    if not os.path.exists(DATA_SRC_ROOT):
        raise ValueError("Wrong directory: %s" % DATA_SRC_ROOT)
    dirs = os.listdir(DATA_SRC_ROOT)
    dirs.remove(get_today_date())  # remove today
    for d in dirs:
        collect_oneday(d)


def collect_oneday(d):
    data_path = os.path.join(DATA_DEST_ROOT, d)
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    src_dir = os.path.join(DATA_SRC_ROOT, d)
    if not os.path.exists(src_dir):
        raise ValueError("Wrong directory: %s" % src_dir)
    for k in os.listdir(src_dir):
        if 'kof97' in k:
            f = ''.join([src_dir, '/', k, '/', 'ledo_game.log'])
            if os.path.isfile(f):
                copyfile(f, ''.join([data_path, '/', k, '_ledo_game.log']))

    ext = Extract(d, DATA_DEST_ROOT)
    ext.run_extract()
    rmtree(data_path, True)
