from functools import lru_cache
from functools import wraps
from logging import getLogger

from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import connections
from flask import Flask
from flask import abort
from flask import jsonify
from flask import render_template
from flask import request
from flask_jsglue import JSGlue
from flask_security import LoginForm
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_security import current_user
from flask_security import login_required
from mongoengine import DoesNotExist
from mongoengine import ValidationError

from enerknol import config
from enerknol import forms
from enerknol import models

app = Flask(__name__)
app.config.from_object(config)

# from https://goo.gl/JRA5Zi
jsglue = JSGlue(app)

# from https://goo.gl/v9VnRp
connections.create_connection(hosts=app.config['ELASTIC_HOSTS'])

# from https://goo.gl/U5ktnS and https://goo.gl/EextKx
models.db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(models.db, models.User, models.Role)
security = Security(app, user_datastore,
                    login_form=LoginForm, register_form=forms.RegisterForm)


# from https://goo.gl/MjecbL
models.mongo.init_app(app)


@lru_cache(maxsize=256)
def user_exists(access_token):
    user = models.User.query.filter_by(access_token=access_token).first()
    return user is not None


def token_required(decorated_view):
    @wraps(decorated_view)
    def decorator(*args, **kwargs):
        access_token = request.headers.get('X-Access-Token')
        if not access_token:
            return jsonify(status='error', message='Missing auth token'), 403

        if not user_exists(access_token):
            return jsonify(status='error', message='Unknown user'), 403

        return decorated_view(*args, **kwargs)

    return decorator


@app.before_first_request
def setup_database():
    models.db.create_all()

    if app.config['TESTING']:
        test_user_email = app.config['TEST_USER_EMAIL']
        test_user_password = app.config['TEST_USER_PASSWORD']
        test_user_access_token = app.config['TEST_USER_ACCESS_TOKEN']

        user = user_datastore.find_user(email=test_user_email)
        if not user:
            user_datastore.create_user(
                email=test_user_email,
                password=test_user_password,
                access_token=test_user_access_token)
            user_datastore.commit()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('search.html')

    return render_template('index.html')


@app.route('/document/<document_id>')
@login_required
def document(document_id):
    try:
        doc = models.Document.objects.get(id=document_id)
    except (DoesNotExist, ValidationError):
        return abort(404, 'Document not found')

    return render_template('document.html', document=doc)


@app.route('/api/documents', methods=['POST'])
@token_required
def post_document():
    request_json = request.get_json(silent=True)
    if not request_json:
        return jsonify(status='error', message='Request is not JSON'), 400

    document_text = request_json.get('document')
    if not document_text:
        return jsonify(status='error', message='Missing key: document'), 400

    doc = models.Document(content=document_text).save()
    doc_id = str(doc.id)

    # from https://goo.gl/v9VnRp
    models.DocumentIndex(id=doc_id, content=document_text).save()

    return jsonify(status='created', document_id=doc_id), 201


@app.route('/api/documents/search/<query>')
@token_required
def get_search_results(query):
    offset = max(int(request.args.get('offset', '0')), 0)
    limit = min(int(request.args.get('limit', '20')), 100)

    search = Search()\
        .source(['id'])\
        .query('match', content=query)\
        .highlight('content')

    search = search[offset:offset+limit]

    results = [{'id': result.id,
                'highlights': list(result.meta.highlight.content)}
               for result in search.execute()]

    return jsonify(status='success', results=results), 200


if __name__ == '__main__':
    # from https://goo.gl/c7i9zv
    gunicorn_logger = getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
