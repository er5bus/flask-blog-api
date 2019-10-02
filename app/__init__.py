from flask import Flask
from flask_jwt_extended import JWTManager
from config import config
from flask_mongoengine import MongoEngine
from flask_marshmallow import Marshmallow


mongo = MongoEngine()
ma = Marshmallow()
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mongo.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app