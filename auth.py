from flask import Blueprint, render_template, request, redirect, session, url_for
from redis_config import r

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if r.hexists("users", username):
            return "Username already exists"
        r.hset("users", username, password)
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        stored_password = r.hget("users", username)
        if stored_password and stored_password == password:
            session['username'] = username
            return redirect(url_for('rooms'))
        return "Invalid credentials"
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
