from flask import redirect, render_template, url_for
from flask_login import current_user

from .. import db
from . import bp
from .forms import CategoryForm
from .models import Category


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/categories", methods=["GET", "POST"])
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        categ = Category.from_name(
            username=current_user.username, name=form.name.data, hidden=form.hidden.data
        )
        db.session.add(categ)
        db.session.commit()
        return redirect(url_for("tally.categories"))
    return render_template(
        "categories.html", title="Categories", form=form, categories=current_user.categories
    )


@bp.route("/edit_category/<string:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    category = Category.query.get(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.hidden = form.hidden.data
        db.session.commit()
        return redirect(url_for("tally.categories"))
    return render_template("edit_category.html", title="Edit Category", form=form)


@bp.route("/delete_category/<string:category_id>", methods=["GET", "POST"])
def delete_category(category_id):
    # TODO: Add confirmation via bootstrap modal
    category = Category.query.get(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("tally.categories"))
