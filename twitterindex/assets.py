from os import path

from flask import send_from_directory
from flask.ext.assets import Environment, Bundle


def init_app(app):
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
            'underscore/underscore.js',
            'backbone/backbone.js',
            'moment/min/moment-with-locales.js',
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
