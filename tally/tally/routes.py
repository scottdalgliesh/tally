from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc
from werkzeug import Response
from werkzeug.utils import secure_filename

from ..extensions import db
from .forms import BillForm, CategoryForm, MultipleBillCategoryForm, StatementForm
from .models import Bill, Category
from .parse import parse_statement
from .review import UserBillData

bp = Blueprint(
    "tally",
    __name__,
    template_folder="templates",
    static_folder="static",
)


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

    uncategorized_bills = (
        db.session.query(Bill)
        .filter_by(user_id=current_user.id, category_id=None)
        .order_by(desc(Bill.date))
    ).all()

    # form choices must be dynamically assigned after instantiation
    data = {"categories": [{"category": -1} for _ in uncategorized_bills]}
    form = MultipleBillCategoryForm(data=data)
    for sub_form in form.categories:
        sub_form.category.choices = current_user.get_category_options()

    if form.validate_on_submit():
        categorized_counter = 0
        for bill, field in zip(uncategorized_bills, form.categories, strict=True):
            # ignore entries which have not been modified (i.e. still selected as blank)
            # -1 used for un-categorized items since None is not compatible with SelectField
            if field.category.data == -1:
                continue
            bill.category_id = field.category.data
            categorized_counter += 1

        db.session.commit()
        flash(f"{categorized_counter} bill(s) categorized successfully.", "success")
        return redirect(url_for("tally.review_all"))

    return render_template(
        "categorize.html",
        title="Categorize",
        transactions=uncategorized_bills,
        form=form,
        zip=zip,
    )


@bp.route("/review_all", methods=["GET"])
@login_required
def review_all() -> str | Response:
    """Review categorized transactions."""
    # pylint: disable=singleton-comparison
    transactions = (
        db.session.query(Bill)
        .filter(Bill.user_id == current_user.id, Bill.category_id != None)
        .order_by(desc(Bill.date))
        .all()
    )
    return render_template(
        "bills.html",
        title="Review All",
        transactions=transactions,
    )


@bp.route("/edit_bill/<int:bill_id>", methods=["GET", "POST"])
@login_required
def edit_bill(bill_id: int) -> str | Response:
    """Edit an existing bill."""
    bill = Bill.query.get(bill_id)
    form = BillForm(
        date=bill.date, description=bill.descr, value=bill.value, category=bill.category_id
    )
    form.category.choices = current_user.get_category_options()

    if form.validate_on_submit():
        bill.date = form.date.data
        bill.descr = form.description.data
        bill.value = form.value.data
        bill.category_id = form.category.data
        db.session.commit()
        flash("bill successfully updated", "success")
        return redirect(url_for("tally.review_all"))

    return render_template("edit_bill.html", title="Edit Bill", form=form)


@bp.route("/new_bill", methods=["GET", "POST"])
@login_required
def new_bill() -> str | Response:
    """Add a new bill."""
    form = BillForm()
    form.category.choices = current_user.get_category_options()
    if form.validate_on_submit():
        category_id = None if form.category.data == -1 else form.category.data
        bill = Bill(
            date=form.date.data,
            descr=form.description.data,
            value=form.value.data,
            category_id=category_id,
            user_id=current_user.id,
        )
        db.session.add(bill)
        db.session.commit()
        flash(f"New bill ({form.description.data}) added successfully.", "success")
        return redirect(url_for("tally.new_bill"))
    return render_template("new_bill.html", title="New Bill", form=form)


@bp.route("/delete_bill/<int:bill_id>", methods=["GET", "POST"])
@login_required
def delete_bill(bill_id: int) -> Response:
    """Delete a bill."""
    bill = Bill.query.get(bill_id)
    description = bill.descr
    db.session.delete(bill)
    db.session.commit()
    flash(f"Bill ({description}) deleted successfully.", "success")
    return redirect(url_for("tally.review_all"))


@bp.route("/review_summary")
@login_required
def review_summary() -> str | Response:
    """Review a per-category monthly summary."""
    user_data = UserBillData(user=current_user)
    try:
        user_data.filter_first_and_last_month()
    except ValueError:
        if not user_data.data.empty:
            flash(
                """
            Note: the results below include data from the first and last months on record, which
            may be incomplete. Once enough data exists, these months will be excluded by default
            to ensure overall averages are as accurate as possible.
            """,
                "warning",
            )
    summary = user_data.summarize()
    styles = {
        "selector": ".col_heading, td",
        "props": f"text-align: right; width: {1/(len(summary.columns)+1)*100}%;",
    }
    summary_html = (
        summary.style.format(formatter="{:,.2f}")
        .set_table_attributes('class="table table-striped table-hover"')
        .set_table_styles([styles])
        .to_html()
    )
    return render_template(
        "review_summary.html",
        title="Summary",
        empty=user_data.data.empty,
        summary_html=summary_html,
    )
