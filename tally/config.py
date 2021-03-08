import os
from pathlib import Path

root = Path.home() / 'AppData/Local/tally'
if not root.exists():
    root.mkdir(parents=True)

# conditionally switch to testing database based on environment variable
if os.environ.get('TALLY_TESTING') == '1':
    DB_URL = root / 'test.db'
else:
    DB_URL = root / 'tally.db'


class Config():
    # in a production environment, move SECRET_KEY to environment variable
    SECRET_KEY = '4455c5ee905b7570bc26cf8fee1fac88'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_URL}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
