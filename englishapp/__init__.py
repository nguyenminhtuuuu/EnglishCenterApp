from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # định vị vị trí của project hiện tại

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/ecdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
