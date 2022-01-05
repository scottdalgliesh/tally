# pylint: disable=[missing-class-docstring]
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, data_required

from .models import Category


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

    def validate_file(self, file: FileField) -> None:
        """Allow only file extension of '.pdf'."""
        if file.data:
            extension = file.data.filename.split(".")[-1].lower()
            if extension != "pdf":
                raise ValidationError("Only PDF documents are accepted.")
