import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:cgbpc0i7Osf3@localhost/cupcakeapp"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
