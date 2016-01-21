import time
import os
from db_utils import DB_model


def time_str_to_int(t=''):
    '''
    the time string must with the format "2016-01-18"
    '''
    return time.mktime(time.strptime(t, "%Y-%m-%d"))


def time_int_to_str(t=0):
    '''
    transform the timestamp to time string
    '''
    return time.strftime("%Y-%m-%d",time.localtime(t))


def get_db_inst_of_day(dbname):
    '''
    get the date of the dbname, because our datebase created
    based the date.
    '''
    if not os.path.isfile(dbname):
        return None

    basename = os.path.basename(dbname)
    d = basename.split('-')[0]
    return DB_model(d)
