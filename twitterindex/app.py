from flask import Flask, render_template

from . import config
from . import assets


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

assets.init_app(app)


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
