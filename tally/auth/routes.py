from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug import Response

from ..extensions import bcrypt, db
from .forms import UserLoginForm, UserRegisterForm, UserUpdateForm
from .models import User

bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)


def is_safe_url(next_url: str) -> bool:
    """Verify next_url is an internal application route prior to redirection."""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.methods is None:
            continue
        if "GET" in rule.methods and "static" not in rule.rule:
            routes.append(rule.rule)
    return next_url in routes


@bp.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for("tally.home"))

    form = UserRegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account for {form.username.data} created.", "success")
        return redirect(url_for("tally.home"))
    return render_template("register.html", title="Register", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for("tally.home"))

    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_url = request.args.get("next")
            if next_url and not is_safe_url(next_url):
                return abort(400)
            return redirect(next_url or url_for("tally.home"))
        flash("Login failed. Please check username and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@bp.route("/logout")
@login_required
def logout() -> Response:
    """User logout page."""
    logout_user()
    return redirect(url_for("tally.home"))


@bp.route("/account", methods=["GET", "POST"])
@login_required
def account() -> str | Response:
    """User account page."""
    form = UserUpdateForm()
    if form.validate_on_submit():
        current_user.username = form.username.data  # pylint: disable=[assigning-non-slot]
        db.session.commit()
        flash("Account information updated.", "success")
    if request.method == "GET":
        form.username.data = current_user.username
    return render_template("account.html", title="Account", form=form)
