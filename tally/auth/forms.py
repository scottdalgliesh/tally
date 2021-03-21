from wtforms_alchemy import ModelForm

from .models import User


class UserRegisterForm(ModelForm):
    class Meta:
        model = User
