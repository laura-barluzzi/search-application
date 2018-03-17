from flask import Flask
from flask import render_template
from flask_security import LoginForm
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from logging import getLogger

from enerknol import config
from enerknol import models
from enerknol.forms import RegisterForm

app = Flask(__name__)
app.config.from_object(config)

# from https://goo.gl/U5ktnS and https://goo.gl/EextKx
models.db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(models.db, models.User, models.Role)
security = Security(app, user_datastore,
                    login_form=LoginForm, register_form=RegisterForm)


@app.before_first_request
def setup_database():
    models.db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # from https://goo.gl/c7i9zv
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
