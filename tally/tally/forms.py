# pylint: disable=[missing-class-docstring]
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.sql import elements
from wtforms import (
    BooleanField,
    DecimalField,
    FieldList,
    FloatField,
    Form,
    FormField,
    HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.fields.html5 import DateField
from wtforms.validators import Length, data_required, optional

from .models import Bill, Category


class CategoryForm(FlaskForm):
    id = HiddenField("id")
    name = StringField("name", validators=[data_required(), Length(1, 30)])
    hidden = BooleanField("hidden field")
    submit = SubmitField("Save")

    def validate_name(self, name: StringField) -> None:
        """Allow category name to equal existing, otherwise ensure it is unique."""
        # if 'id' provided to form, allow name to equal existing value
        if self.id.data and name.data.lower() == Category.query.get(self.id.data).name.lower():
            return

        # verify category name is unique
        existing_categories = [categ.name.lower() for categ in current_user.categories]
        if name.data.lower() in existing_categories:
            raise ValidationError("Category already exists.")


class StatementForm(FlaskForm):
    file = FileField("file", validators=[FileRequired()])
    submit = SubmitField("Parse")

    def validate_file(self, file: FileField) -> None:  # pylint: disable=no-self-use
        """Allow only file extension of '.pdf'."""
        if file.data:
            extension = file.data.filename.split(".")[-1].lower()
            if extension != "pdf":
                raise ValidationError("Only PDF documents are accepted.")


class BillCategoryForm(Form):
    # This form is intended to be used as a FormField, so it inherits from Form
    # instead of FlaskForm to avoid generating a CSRF key for each instance.
    # Note: dynamic choices must be assigned after instantiation
    category = SelectField("Select a category", choices=[], coerce=int)


class MultipleBillCategoryForm(FlaskForm):
    categories = FieldList(FormField(BillCategoryForm))
    submit = SubmitField("Save")


class BillForm(FlaskForm):
    date = DateField("Date", validators=[data_required()])
    description = StringField("Description", validators=[data_required()])
    value = FloatField("Value", validators=[data_required()])
    category = SelectField("Select a category", choices=[], coerce=int)
    submit = SubmitField("Save")


class BillFilterForm(FlaskForm):
    start_date = DateField("Start Date", validators=[optional()])
    end_date = DateField("End Date", validators=[optional()])
    keywords = StringField("Enter search keyword(s)")  # TODO: allow regex
    categories = SelectMultipleField("Select one or more category", choices=[], coerce=int)
    min_value = DecimalField("Minimum value", validators=[optional()])
    max_value = DecimalField("Maximum value", validators=[optional()])
    exclude_hidden = BooleanField("Exclude hidden items", default="checked")
    submit = SubmitField("Apply Filters")

    def generate_filters(self, user_id: int) -> list[elements.BinaryExpression]:
        """Convenience method to build search query from form data."""
        return Bill.generate_filters(
            user_id=user_id,
            start_date=self.start_date.data,
            end_date=self.end_date.data,
            description=self.keywords.data,
            categories=self.categories.data,
            exclude_hidden=self.exclude_hidden.data,
            min_value=self.min_value.data,
            max_value=self.max_value.data,
        )
