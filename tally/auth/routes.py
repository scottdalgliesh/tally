from flask import render_template

from . import bp


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/login')
def login():
    return render_template('login.html')
