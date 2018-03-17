from logging import getLogger

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_security import LoginForm
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security

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


# from https://goo.gl/MjecbL
models.mongo.init_app(app)


@app.before_first_request
def setup_database():
    models.db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/documents', methods=['POST'])
def ingest():
    request_json = request.get_json(silent=True)
    if not request_json:
        return jsonify(status='error', message='Request is not JSON'), 400

    document_text = request_json.get('document')
    if not document_text:
        return jsonify(status='error', message='Missing key: document'), 400

    document = models.Document(content=document_text).save()
    document_id = str(document.id)

    # put to elastic

    return jsonify(status='created', document_id=document_id), 201


if __name__ == '__main__':
    # from https://goo.gl/c7i9zv
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
