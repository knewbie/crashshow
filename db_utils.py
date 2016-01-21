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
            self.dbname = ''.join([DB_PATH, date, '-crashinfo.db'])
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
