from flask import Flask
from flask import render_template
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from logging import getLogger

from enerknol import config
from enerknol import models
from enerknol.database import init_db

app = Flask(__name__)
app.config.from_object(config)

# from https://goo.gl/EJuMq7
db = SQLAlchemy(app)
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)


@app.before_first_request
def setup_database():
    init_db()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # from https://goo.gl/iNLNLx
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
