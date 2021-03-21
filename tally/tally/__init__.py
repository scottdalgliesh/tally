from flask import Blueprint

bp = Blueprint(
    'tally',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import models, routes  # nopep8
