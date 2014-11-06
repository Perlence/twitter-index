from datetime import datetime

from flask import Flask, render_template
from flask.ext import restful
from whoosh.qparser import QueryParser

from . import assets
from . import config
from .models import TweetIndex


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

assets.init_app(app)
api = restful.Api(app)


class Query(restful.Resource):
    parser = QueryParser('text', TweetIndex.schema)

    def get(self, query):
        terms = self.parser.parse(query)
        result = {'tweets': []}
        with TweetIndex.searcher() as searcher:
            top_items = searcher.search(terms)
            for hit in top_items:
                item = {}
                for key, value in hit.iteritems():
                    if key == 'id_str':
                        key = 'id'
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    item[key] = value
                result['tweets'].append(item)
        return result

api.add_resource(Query, '/query/<path:query>')


@app.route('/')
def index():
    return render_template('index.html')


def start(debug=False):
    host = config.HOST
    port = config.PORT
    if host is None:
        host = '127.0.0.1' if debug else '0.0.0.0'
    app.debug = debug
    app.run(host=host, port=port)


def debug():
    start(debug=True)
