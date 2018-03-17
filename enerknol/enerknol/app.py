from logging import getLogger

from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Search
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_security import LoginForm
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from mongoengine import DoesNotExist
from mongoengine import ValidationError

from enerknol import config
from enerknol import models
from enerknol.forms import RegisterForm

app = Flask(__name__)
app.config.from_object(config)

# from https://goo.gl/v9VnRp
connections.create_connection(hosts=config.ELASTIC_HOSTS)

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
def post_document():
    request_json = request.get_json(silent=True)
    if not request_json:
        return jsonify(status='error', message='Request is not JSON'), 400

    document_text = request_json.get('document')
    if not document_text:
        return jsonify(status='error', message='Missing key: document'), 400

    document = models.Document(content=document_text).save()
    document_id = str(document.id)

    # from https://goo.gl/v9VnRp
    models.DocumentIndex(id=document_id, content=document_text).save()

    return jsonify(status='created', document_id=document_id), 201


@app.route('/api/documents/<document_id>')
def get_document(document_id):
    try:
        document = models.Document.objects.get(id=document_id)
    except (DoesNotExist, ValidationError):
        return jsonify(status='error', message='Document not found'), 404

    return jsonify(status='success', content=document.content), 200


@app.route('/api/documents/search/<query>')
def get_search_results(query):
    offset = int(request.args.get('offset', '0'))
    size = int(request.args.get('size', '20'))

    search = Search().source(['id']).query('match', content=query)
    search = search[offset:offset+size]
    results = [result.id for result in search.execute()]

    return jsonify(status='success', results=results), 200


if __name__ == '__main__':
    # from https://goo.gl/c7i9zv
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
