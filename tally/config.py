from pathlib import Path

ROOT = Path.home() / 'AppData/Local/tally'
if not ROOT.exists():
    ROOT.mkdir(parents=True)
DB_URL = ROOT / 'tally.db'
TEST_DB_URL = ROOT / 'test.db'


class Config:
    # in a production environment, move SECRET_KEY to environment variable
    SECRET_KEY = '4455c5ee905b7570bc26cf8fee1fac88'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_URL}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB_URL}'
    TESTING = True
