import os
import time
from datetime import datetime, timedelta
from db_utils import DB_model
from data_collect import Extract


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
    ext = Extract(today)
    ext.run_extract()
    return True


def check_upadte_elapse(pre):
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
    pre = pre and datetime.fromtimestamp(pre) or datetime.now()
    dif = datetime(1970, 1, 1) + (now - pre)
    if now.day != pre.day:
        return 2
    elif dif.hour > 2:
        return 1
    else:
        return 0, '%s-%02d-%02d %02d:%02d:%02d' %(pre.year,pre.month,pre.day,pre.hour,pre.minute,pre.second)


def collect_today_data():
    from shutil import copyfile
    DATA_PATH = os.path.join('/home/m-out-ll/crash_data',get_today_date())
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    src_dir = os.path.join('/export/dump/backup',get_today_date())
    if not os.path.exists(src_dir):
        raise ValueError("directory(%s) doesn't existed" % src)
    files = os.listdir(DATA_PATH)
    for k in os.listdir(src_dir):
        if 'kof97' in k and k not in files:
            copyfile(os.path.join(src_dir, k), os.path.join(DATA_PATH,k))
