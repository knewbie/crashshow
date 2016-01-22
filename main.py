# -*-:coding = utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from models import db_handler
from utils import *

DEBGU = True
SECRET_KEY = 'test key'
 
user_dict = {
        'admin':'admin',
        'kevin':'kevinlee',
        'lwn':'lwn1234',
        'ff':'ff1234',
        'mxc':'mxc1234'}


app = Flask(__name__)
app.config.from_object(__name__)


# @app.before_request
# def before_request():
    # g.db = connect_db()


# @app.teardown_request
# def teardown_request(exception):
    # db.close()


@app.route('/')
def index():

    status = check_today_db()
    if not status:
        flash("Today's data hasn't be create, Please Create It now")
    return render_template('main.html', status=status, data=None)


@app.route('/pulldata')
def pulldata():
    update_today_db()
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
    dat = [dict(id=r[0], hash=r[1], info=r[2], times=r[3], status=r[4], author=r[5])\
            for r in db.get_crash_data()]
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


@app.route('/show_detail/<date>', methods=['GET'])
def show_detail(date):
    row = db_handler.get_one_day_info(time_str_to_int(date))
    print date, time_str_to_int(date)
    if not row:
        flash("No data of the day( %s )" % date)
        return redirect(url_for('index'))

    session['req_today_db'] = row[0]
    db = get_db_inst_of_day(row[0])

    data = [dict(id=r[0], hash=r[1], info=r[2], times=r[3], status=r[4], author=r[5])
            for r in db.get_crash_data()]
    return render_template('detail.html', data=data)


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
    #rows = db_handler.get_all()
    #entries = [dict(date=time_int_to_str(row[0])) for row in rows]
    #return render_template('main.html', entries=entries)
    
    flash("Coming soon...")
    return redirect(url_for('index'))


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




if __name__ == '__main__':
    #app.run("0.0.0.0")
    app.run(debug=True)
