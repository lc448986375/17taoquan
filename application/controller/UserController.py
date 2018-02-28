from flask import request, redirect, url_for, render_template, make_response, session
from application import app, db
from functools import wraps

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = None
        if 'user_name' in session:
            user = session['user_name']
        if user is None or len(user) == 0:
            return redirect(url_for('login', next = request.url))
        return func(*args, **kwargs)
    return decorated_function

@app.route('/user', methods = ['GET'])
@login_required
def user():
    site_info = {
        'title':'登陆'
    }
    url_args = {
    
    }
    return render_template('user.html', site_info = site_info, url_args = url_args)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    method = request.method
    if method == 'GET':
        site_info = {
            'title':'登陆'
        }
        url_args = {
        
        }
        return render_template('login.html', site_info = site_info, url_args = url_args)
    elif method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']

        if valid_user(user_name, password):
            session['user_name'] = user_name
            return redirect(url_for('user'))

        else:
            return redirect(url_for('login'))

def valid_user(user_name, password):
    if user_name == 'admin' and password == 'admin':
       return True

    return False
