import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)  # định vị vị trí của project hiện tại


app.secret_key = "dshfuidsfjdshfjdh"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/ecdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)

cloudinary.config(cloud_name='deeqcwnpm',
                  api_key='642514279843968',
                  api_secret='iOM3oFrZpEwBIrnkHdaPfmT8njY',)

login = LoginManager(app)