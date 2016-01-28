# -*-:coding = utf-8 -*-

from hashlib import sha1
from flask import request, session,  redirect, url_for,  render_template, flash
from app import app
from models import db_handler
from utils import *


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
    dat = [dict(no=r+1, id=data[r][0], hash=data[r][1], info=data[r][2], times=data[r][3], status=data[r][4], author=data[r][5]) for r in range(len(data))]
    t = db_update_time_to_str(db.get_last_update())
    return render_template('main.html', status=status, data=dat, time=t)


@app.route('/update')
def update():
    db = get_db_inst_of_day(get_today_date())
    ts = db.get_last_update()
    ret = check_upadte_elapse(ts)
    if ret[0] == 2:
        flash("A new day has begin, Please Create the New db")
        return render_template('main.html', status=False, data=None)
    elif ret[0] == 0:
        warn = ["Don't update so often !", "Last update:  %s" % ret[1]]
        return render_template('main.html', status=True, data=None, warn=warn)
    elif ret[0] == 1:
        update_today_db(True)
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
    tip = None
    st = db.get_status(id)
    if st[0] == 0:
        db.refresh(id, session.get('username'), 1)
    elif st[0] == 1 and st[1] != session.get('username'):
        tip = ["This bug has been processed by <strong style='color:red'>%s </strong>" % st[1]]
    data = db.get_crash_data()
    dat = [dict(no=r+1, id=data[r][0], hash=data[r][1], info=data[r][2], times=data[r][3], status=data[r][4], author=data[r][5]) for r in range(len(data))]
    return render_template('main.html', data=dat, warn=tip)


@app.route('/doit/<id>', methods=['GET'])
def doit(id):
    if not session.get('login_in'):
        flash("Please Login Your Account, then achieve your glories!")
        return redirect(url_for('show_today'))

    if not session.get('req_today_db'):
        flash("Oops: Missing db info ...")
        return redirect(url_for('index'))

    db = get_db_inst_of_day(session.get('req_today_db'))

    tip = None
    st = db.get_status(id)
    if st[1] != session.get('username'):
        tip = ["This bug has been processed by <strong style='color:red'>%s </strong>. Don't rob other's glory" % st[1]]
    else:
        db.refresh(id, session.get('username'), 2)
    data = db.get_crash_data()
    dat = [dict(no=r+1, id=data[r][0], hash=data[r][1], info=data[r][2], times=data[r][3], status=data[r][4], author=data[r][5]) for r in range(len(data))]
    return render_template('main.html', data=data, warn=tip)



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
    return render_template('history.html', all_days=days, data=None)


@app.route('/history_detail/<date>', methods=['GET'])
def history_detail(date):
    db = get_db_inst_of_day(date)
    data = db.get_crash_data()
    if not data:
        flash("No data of the day( %s )" % date)
        return redirect(url_for('history'))

    all_days = [dict(date=r[1]) for r in db_handler.get_all() if r[1] != get_today_date()]
    dat = [dict(id=r+1, hash=data[r][1], info=data[r][2], times=data[r][3], status=data[r][4], author=data[r][5]) for r in range(len(data))]
    return render_template('history.html', all_days=all_days, data=dat, day=date)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pw = request.form.get('password', '').strip()
        if uname == '' or db_handler.check_user_name_valid(uname):
            flash('Invalid username')
            print 'Wrong uname: %s' % uname
        elif pw == '' or sha1(pw).hexdigest() != db_handler.get_user_passwd(uname):
            flash('Invalid password')
            print "Wrong pw: %s" % pw
        else:
            session['login_in'] = True
            session['username'] = uname
            flash("You have logged in. Now you can take care the crash info. Sign out on the top right.Have a fun.. ^_^")
            return redirect(url_for('show_today'))
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('login_in', None)
    session.pop('username', None)
    #session.pop('req_today_db', None)
    flash('You have signed out.')
    return redirect(url_for('index'))


@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if not session.get('login_in'):
        flash('Please login Admin account to add user')
        return redirect(url_for('index'))

    if request.method == 'GET':
        tip = "Add A New User"
        return render_template('user.html', status=True, data=None, tip=tip)
    elif request.method == 'POST':
        uname = request.form.get('username', '').strip()
        pw = request.form.get('password', '').strip()
        pw1 = request.form.get('password1', '').strip()
        if uname.strip() == '':
            flash('Please input the valid username')
            return render_template('user.html', status=True, data=None, warn=None)
        elif not db_handler.check_user_name_valid(uname):
            msg = ['Username: <strong style="color:red"> %s </strong>  has beed registered, Please input another!' % uname]
            return render_template('user.html', status=True, data=None, warn=msg)
        elif pw != pw1:
            msg = ["Two passwords don't identify. Please check it agaion"]
            return render_template('user.html', status=True, data=None, warn=msg)
        else:
            db_handler.save_user(uname, sha1(pw.strip()).hexdigest())
            return redirect(url_for('index'))
