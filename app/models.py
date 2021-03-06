# -*-: coding = utf-8 -*-

import sqlite3
import os

DB_NAME = './db/all_db_info.db'


class All_db_model(object):
    '''
    this model class used for the web
    '''

    def __init__(self, dbname):
        self.db_name = dbname
        if not os.path.isfile(dbname):
            conn = sqlite3.connect(dbname)
            cur = conn.cursor()
            cur.executescript("""
                    CREATE TABLE all_db_info(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dbdate INTEGER NOT NULL,
                    dbname STRING NOT NULL,
                    create_time STRING NOT NULL);
                    """)
            cur.executescript("""
                    CREATE TABLE users(
                    username STRING PRIMARY KEY,
                    password STRING NOT NULL);
                    """)
            conn.commit()
            conn.close()

    def get_one_day_info(self, date):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        row = cur.execute('select dbname from all_db_info where dbdate = ?', (date,)).fetchone()
        cur.close()
        conn.close()
        return row

    def get_recent_day_info(self, ndays):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        rows = cur.execute("select dbname from all_db_info order by dbdate desc limit ?", (ndays,)).fetchall()
        cur.close()
        conn.close()
        return rows

    def get_all(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        rows = cur.execute("select dbname, create_time from all_db_info order by dbdate desc").fetchall()
        cur.close()
        conn.close()
        return rows

    def delete(self, dbname):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute("delete from all_db_info where dbname=?", (dbname,))
        conn.commit()
        conn.close()

    def check_user_name_valid(self, username):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        users =[u[0] for u in cur.execute('select username from users').fetchall()]
        conn.close()
        if username in users:
            return False
        else:
            return True

    def get_user_passwd(self, uname):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        passwd = cur.execute('select password from users where username=?', (uname,)).fetchone()
        conn.close()
        return passwd[0]

    def save_user(self, uname, passwd):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('insert into users values (?,?)', (uname, passwd))
        conn.commit()
        conn.close()

db_handler = All_db_model(DB_NAME)
