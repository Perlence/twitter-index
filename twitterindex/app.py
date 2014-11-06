from os import path

from flask import Flask, send_from_directory, render_template
from flask.ext.assets import Environment, Bundle

from . import config


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

env = Environment(app)
env.load_path = [
    path.join(path.dirname(__file__), 'scss'),
    path.join(path.dirname(__file__), 'coffee'),
    path.join(path.dirname(__file__), 'bower_components'),
]
js_bundle = Bundle(
    Bundle(
        'jquery/dist/jquery.js',
        'bootstrap-sass-official/assets/javascripts/bootstrap.js',
        output='js_requirements.js'),
    Bundle(
        'index.coffee',
        filters=['coffeescript'],
        output='js_index.js'))
css_bundle = Bundle(
    'all.scss',
    filters=['scss', 'autoprefixer'],
    output='css_all.css')
env.config['sass_load_paths'] = [
    path.join(
        path.dirname(__file__),
        'bower_components/bootstrap-sass-official/assets/stylesheets/'),
]
env.register('js_all', js_bundle)
env.register('css_all', css_bundle)


@app.route('/static/fonts/<path:fontname>')
def static_fonts(fontname):
    directory = path.join(
        path.dirname(__file__),
        'bower_components/bootstrap-sass-official/assets/fonts/bootstrap')
    return send_from_directory(directory, fontname)


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
