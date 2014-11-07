from bson import json_util
from flask import Flask, render_template, make_response
from flask.ext.restful import Api, Resource
from flask.ext.mongoengine import MongoEngine
from whoosh.qparser import QueryParser

from . import assets
from .models import Tweet, TweetIndex


app = Flask(__name__)
app.config.from_pyfile('config.py')

assets.init_app(app)
api = Api(app)
db = MongoEngine(app)


@api.representation('application/json')
def json(data, code, headers=None):
    resp = make_response(json_util.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


class Query(Resource):
    parser = QueryParser('text', TweetIndex.schema)

    def get(self, query):
        terms = self.parser.parse(query)
        result = {'tweets': []}
        with TweetIndex.searcher() as searcher:
            # Could use some concurrent processing
            result['tweets'] = [Tweet.objects.get(id=hit['id']).to_mongo()
                                for hit in searcher.search(terms)]
        return result

api.add_resource(Query, '/query/<path:query>')


@app.route('/')
def index():
    return render_template('index.html')


def start(debug=False):
    host = app.config['HOST']
    if host is None:
        host = '127.0.0.1' if debug else '0.0.0.0'
    app.debug = debug
    app.run(host=host)


def debug():
    start(debug=True)
