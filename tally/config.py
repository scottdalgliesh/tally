from pathlib import Path

ROOT = Path.home() / 'AppData/Local/tally'
if not ROOT.exists():
    ROOT.mkdir(parents=True)
DB_URL = ROOT / 'tally.db'


class Config:
    # in a production environment, move SECRET_KEY to environment variable
    SECRET_KEY = '4455c5ee905b7570bc26cf8fee1fac88'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_URL}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
