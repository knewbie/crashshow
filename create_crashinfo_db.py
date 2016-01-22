# -*-coding:utf8 -*-

import sqlite3
import time
import os
import sys

DB_PATH = './db/'

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
            self.conn = sqlite3.connect(self.dbname)
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
            self.conn.commit()
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
        cur.execute('insert into hash_info (hash_value, count) values (?, ?)', \
                (hash_value, count))
        self.conn.commit()

    def fetch_all_hash(self):
        data = {}
        cur = self.conn.cursor()
        for row in cur.execute('select hash_value,count from hash_info').fetchall():
            data[row[0]] = row[1]
        return data

    def update(self, hash_value='', times=0):
        cur = self.conn.cursor()
        cur.execute('update crash_info set times= ? where hash_value = ? ', (hash_value, times))
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
# -*-coding:utf8 -*-

import sqlite3

DB_PATH = './db/'


class DB_model(object):
    """
        Datebase class with db operation
    """
    def __init__(self, date=None):
        if date is not None:
            self.dbname = ''.join([DB_PATH, date, '.db'])
        else:
            raise (ValueError, 'date needed!!')

    def fetch_all_hash(self):
        data = {}
        conn = sqlite3.connect(self.dbname,5)
        cur = conn.cursor()
        for row in cur.execute('select (hash_value,count) from hash_info').fetchall():
            data[row[0]] = row[1]
        conn.close()
        return data

    def get_crash_data(self):
        conn = sqlite3.connect(self.dbname,5)
        cur = conn.cursor()
        rows = cur.execute("select * from crash_info").fetchall()
        return rows

    def refresh(self, id='', author='', status=0):
        conn = sqlite3.connect(self.dbname,5)
        conn.text_factory = str
        cur = conn.cursor()
        cur.execute('update crash_info set author=?,status=? where id = ?', (author, status, id))
        conn.commit()
        conn.close()
