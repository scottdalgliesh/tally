from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from .. import bcrypt, db
from . import bp
from .forms import UserRegisterForm
from .models import User


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tally.home'))
    form = UserRegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Account for {form.username.data} created.', 'success')
        return redirect(url_for('tally.home'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/login')
def login():
    return render_template('login.html')
