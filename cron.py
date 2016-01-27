#!/usr/bin/env python

import os
import logging
from datetime import datetime, timedelta
from shutil import rmtree
from apscheduler.schedulers.blocking import BlockingScheduler
from app.utils import update_today_db
from config import DATA_DEST_ROOT


logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='app-cron.log',
                filemode='w')


def backup_yestoday_job():
    pre = datetime.now() - timedelta(1)
    d = pre.strftime("%Y-%m-%d")
    logging.info('backup data of %s' % d)
    update_today_db(update=True, date=d)
    data_dir = os.path.join(DATA_DEST_ROOT, d)
    if os.path.exists(data_dir):
        rmtree(data_dir)
        logging.info('Remove dir: %s' % data_dir)

    logging.info('backup data end')


def update_interval_job():
    logging.info("begin update data")
    update_today_db(True)
    logging.info('end update data')


if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(update_interval_job, 'interval', hours=1, id='update_job', start_date='2016-01-27 11:30:00')
    sched.add_job(backup_yestoday_job, 'cron', day_of_week='0-6', hour=0, minute=2, start_date="2016-01-27", id='backup_job')
    sched.start()
