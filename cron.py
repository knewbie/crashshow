from apscheduler.schedulers.blocking import BlockingScheduler
def my_job():
    print 'hello world'
         
sched = BlockingScheduler()
sched.add_job(my_job, 'interval', seconds=5)
sched.start()


# one job to refresh every one hour
# one job to collect the whole data on 58:00 of every day
# ref: http://debugo.com/apscheduler/
