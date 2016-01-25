# -*-:coding = utf-8 -*-
from app import app
from flask import request, session,  redirect, url_for,  render_template, flash
from models import db_handler
from utils import *

user_dict = {
        'admin':'admin',
        'kevin':'kevinlee',
        'lwn':'lwn1234',
        'ff':'ff1234',
        'mxc':'mxc1234'}


@app.route('/')
def index():
    status = check_today_db()
    if not status:
        flash("Today's data hasn't be create, Please Create It now")
    return render_template('main.html', status=status, data=None)


@app.route('/pulldata')
def pulldata():
    ret = update_today_db()
    if not ret:
        flash("System is cllecting data,Please wait for minutes")
        return render_template('main.html', status=False, data=None)

    status = check_today_db()
    flash('Data pull down, Click "Today" to check it!')
    return render_template('main.html', status=status, data=None)


@app.route('/show_today')
def show_today():
    status = check_today_db()
    if not status:
        flash("There is no today's data,please create id")
        return redirect(url_for('index'))

    session['req_today_db'] = get_today_date()

    db = get_db_inst_of_day(get_today_date())
    data = db.get_crash_data()
    if data is None:
        flash("There's no data in the database.")
        return render_template('main.html', status=False, data=None)
    dat = [dict(id=r[0], hash=r[1], info=r[2], times=r[3], status=r[4], author=r[5]) for r in data]
    t = db_update_time_to_str(db.get_last_update())
    return render_template('main.html', status=status, data=dat, time=t)


@app.route('/update')
def update():
    db = get_db_inst_of_day(get_today_date())
    pre = db.get_last_update()
    ret, t = check_upadte_elapse(pre)
    if ret == 2:
        flash("A new day has begin, Please Create the New db")
        return render_template('main.html', status=False, data=None)
    elif ret == 0:
        warn = ["Don't update so often !", "Last update:  %s" % t]
        return render_template('main.html', status=True, data=None, warn=warn)
    elif ret == 1:
        update_today_db()
        flash("Refresh today info")
        return redirect(url_for('show_today'))


@app.route('/takeit/<id>', methods=['GET'])
def takeit(id):
    if not session.get('login_in'):
        flash("Please Login Your Account, then achieve your glories!")
        return redirect(url_for('show_today'))

    if not session.get('req_today_db'):
        flash("Oops: Missing db info ...")
        return redirect(url_for('show_today'))

    db = get_db_inst_of_day(session.get('req_today_db'))
    db.refresh(id, session.get('username'), 1)
    data = [dict(id=r[0], hash=r[1], info=r[2], times=r[3], status=r[4], author=r[5])
            for r in db.get_crash_data()]
    return render_template('main.html', data=data)


@app.route('/doit/<id>', methods=['GET'])
def doit(id):
    if not session.get('login_in'):
        flash("Please Login Your Account, then achieve your glories!")
        return redirect(url_for('show_today'))

    if not session.get('req_today_db'):
        flash("Oops: Missing db info ...")
        return redirect(url_for('index'))

    db = get_db_inst_of_day(session.get('req_today_db'))
    db.refresh(id, session.get('username'), 2)

    data = [dict(id=r[0], hash=r[1], info=r[2], times=r[3], status=r[4], author=r[5])
            for r in db.get_crash_data()]
    return render_template('main.html', data=data)



@app.route('/history')
def history():
    rows = db_handler.get_all()
    days = []
    for r in rows:
        if r[1] == get_today_date():
            continue
        if os.path.isfile(r[0]):
            days.append(dict(date=r[1]))
        else:
            db_handler.delete(r[0])

    if len(days) == 0:
        flash("There is no history data to check")
        return redirect(url_for('index'))
    return render_template('history.html', days=days, data=None)


@app.route('/history_detail/<date>', methods=['GET'])
def history_detail(date):
    db = get_db_inst_of_day(date)
    rows = db.get_crash_data()
    if not rows:
        flash("No data of the day( %s )" % date)
        return redirect(url_for('history'))

    days = [dict(date=r[1]) for r in db_handler.get_all() if r[1] != get_today_date()]

    data = [dict(id=r[0], info=r[2], times=r[3], status=r[4], author=r[5])
            for r in rows]
    return render_template('history.html', days=days, data=data)


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        print request.form['username'], request.form['password']
        if request.form['username'] not in user_dict:
            error = 'Invalid username'
        elif request.form['password'] != user_dict.get(request.form['username']):
            error = 'Invalid password'
        else:
            session['login_in'] = True
            session['username'] = request.form['username']
            flash("You have logged in. Now you can take care the crash info. Sign out on the top right.Have a fun.. ^_^")
            return redirect(url_for('show_today'))
    return render_template('main.html', error=error)


@app.route('/logout')
def logout():
    session.pop('login_in', None)
    session.pop('username', None)
    #session.pop('req_today_db', None)
    flash('You have signed out.')
    return redirect(url_for('index'))
