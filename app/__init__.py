from flask import Flask

app = Flask(__name__)
app.config.from_object('config')


from app import views, models
from app import utils, db_utils, data_collect
