# -*-coding:utf8 -*-

import sqlite3
import time
import os
import sys


DB_PATH = './db/'


class DB_model(object):
    """
        Datebase class with db operation
    """
    def __init__(self, date=None):
        if date is not None:
            self.dbname = ''.join([DB_PATH, date, '.db'])
        else:
            raise ValueError('date needed!!')

    def _check_table_exist(self,tb_name=''):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        tables = cur.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'table'").fetchall()
        conn.close()
        if tb_name in [t[0] for t in tables]:
            print "%s in tables" % tb_name
            return True
        print "%s  not in tables" % tb_name
        return False

    def fetch_all_hash(self):
        data = {}
        if not self._check_table_exist('hash_info'):
            return None
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        for row in cur.execute('select (hash_value,count) from hash_info').fetchall():
            data[row[0]] = row[1]
        conn.close()
        return data

    def get_crash_data(self):
        if not self._check_table_exist('crash_info'):
            return None
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        rows = cur.execute("select * from crash_info order by times desc").fetchall()
        conn.close()
        return rows

    def get_status(self, id):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        item = cur.execute('select status, author from crash_info where id=?', (id,)).fetchone()
        conn.close()
        return item

    def refresh(self, id='', author='', status=0):
        conn = sqlite3.connect(self.dbname)
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute('update crash_info set author=?,status=? where id = ?', (author, status, id))
        conn.commit()
        conn.close()

    def get_last_update(self):
        if not self._check_table_exist('update_info'):
            return None
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        row = cur.execute('select update_time from update_info order by id desc limit 1').fetchone()
        conn.close()
        return row[0]


class Crash_Info_Model(object):
    """
        Datebase class with db operation
    """
    def __init__(self, date=None):
        if date is not None:
            self.dbname = ''.join([DB_PATH, date, '.db'])
            print self.dbname
        else:
            raise (ValueError, 'date needed!!')

        if not os.path.isfile(self.dbname):
            self.conn = sqlite3.connect(self.dbname, 20)
            self.conn.text_factory = str
            cur = self.conn.cursor()
            cur.execute('''
                    CREATE TABLE crash_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash_value TEXT NOT NULL,
                    info TEXT NOT NULL,
                    times INTEGER NOT NULL,
                    status INTEGER,
                    author TEXT ); ''')
            cur.execute('''
                CREATE TABLE hash_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_value TEXT NOT NULL,
                count INTEGER NOT NULL);''')
            cur.execute('''
                    CREATE TABLE update_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_time REAL NOT NULL);''')

            self.conn.commit()
            # store the new db info into the all_db_info database
            all_db_name = ''.join([DB_PATH,'all_db_info.db'])
            if not os.path.isfile(all_db_name):
                print "Wrong db file: %s" % all_db_name
                sys.eixt(1)
            db = sqlite3.connect(all_db_name, 2)
            db.text_factory = str
            cur = db.cursor()
            cur.execute("insert into all_db_info (dbdate,dbname,create_time) values (?,?,?)",\
                    (time.mktime(time.strptime(date, "%Y-%m-%d")), self.dbname, date))
            db.commit()
            db.close()
        else:
            self.conn = sqlite3.connect(self.dbname)
            self.conn.text_factory = str

    def save_info(self, hash_value='', info='', times=0, status=0, author='No body love me'):
        cur = self.conn.cursor()
        cur.execute('insert into crash_info (hash_value, info, times, status, author) values ( ?, ?, ?, ?, ?)', \
                (hash_value, info, times, status, author))
        self.conn.commit()

    def save_hash(self, hash_value='', count=0):
        cur = self.conn.cursor()
        cur.execute('insert into hash_info (hash_value, count) values (?, ?)', (hash_value, count))
        self.conn.commit()
    
    def update_hash(self, hash_value, count):
        cur = self.conn.cursor()
        cur.execute('update hash_info set count=? where hash_value=?', (count, hash_value))
        self.conn.commit()

    def fetch_all_hash(self):
        data = {}
        cur = self.conn.cursor()
        for row in cur.execute('select hash_value,count from hash_info').fetchall():
            data[row[0]] = row[1]
        return data

    def update(self, hash_value='', times=0):
        cur = self.conn.cursor()
        cur.execute('update crash_info set times=(?) where hash_value =(?)', (times, hash_value))
        self.conn.commit()

    def when_update(self):
        cur = self.conn.cursor()
        cur.execute('insert into update_info (update_time) values (?)', (time.time(),))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_db_name(self):
        return self.dbname


def collect_db_info(dbname,dbdate):
    if not os.path.isfile(dbname):
        print "Wrong db file: %s" % dbname
        sys.eixt(1)

    db = ''.join([DB_PATH,'all_db_info.db'])
    if not os.path.isfile(db):
        print "Wrong db file: %s" % dbname
        sys.eixt(1)
    db = sqlite3.connect(db, 2)
    db.text_factory = str
    cur = db.cursor()
    cur.execute("insert into all_db_info (dbdate,dbname,create_time) values (?,?,?)",\
            (time.mktime(time.strptime(dbdate, "%Y-%m-%d")), dbname, dbdate))
    db.commit()
    db.close()
    print "insert all_db_info (%s)" % dbname
