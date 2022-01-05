from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug import Response
from werkzeug.utils import secure_filename

from .. import db
from . import bp
from .forms import CategoryForm, StatementForm
from .models import Bill, Category
from .parse import parse_statement


@bp.route("/")
def home() -> str:
    """Home page."""
    return render_template("home.html")


@bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories() -> str | Response:
    """Display user's existing categories and allow new categories to be created."""
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
@login_required
def edit_category(category_id: int) -> str | Response:
    """Edit an existing category."""
    category = Category.query.get(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.hidden = form.hidden.data
        db.session.commit()
        return redirect(url_for("tally.categories"))
    return render_template("edit_category.html", title="Edit Category", form=form)


@bp.route("/delete_category/<string:category_id>", methods=["GET", "POST"])
@login_required
def delete_category(category_id: int) -> Response:
    """Delete an existing category."""
    category = Category.query.get(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("tally.categories"))


@bp.route("/new_statement", methods=["GET", "POST"])
@login_required
def new_statement() -> str | Response:
    """Parse new statement and add transactions to database (un-categorized)."""
    form = StatementForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = current_app.config["UPLOAD_FOLDER"] / secure_filename(file.filename)
        file.save(filename)
        try:
            transactions = parse_statement(filename)
            for transaction in transactions:
                bill = Bill(
                    date=transaction.Date,
                    descr=transaction.Description,
                    value=transaction.Value,
                    user_id=current_user.id,
                    category=None,
                )
                db.session.add(bill)
            db.session.commit()
            flash(f"{len(transactions)} transactions parsed and added successfully.", "success")
        finally:
            # delete uploaded file after parsing
            filename.unlink()
        return redirect(url_for("tally.categorize"))
    return render_template("new_statement.html", title="New Statement", form=form)


@bp.route("/categorize", methods=["GET", "POST"])
@login_required
def categorize() -> str | Response:
    """Review un-categorized transactions, and apply categories."""
    uncategorized_transactions = db.session.query(Bill).filter_by(
        user_id=current_user.id,
        category_id=None,
    )
    # TODO: add dynamic fields as described here: https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms
    return render_template(
        "categorize.html",
        title="Categorize",
        transactions=uncategorized_transactions,
    )
