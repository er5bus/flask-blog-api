from . import api
from .. import jwt
from werkzeug.exceptions import HTTPException


@api.errorhandler(HTTPException)
def handle_exception(e):
    if e.code == 500:
        from ...flasky import app
        app.logger.error(e)
    return _error_handler(e.code, e.description)


@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return _error_handler(422, error_string)


@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    return _error_handler(401, error_string)


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return _error_handler(401, 'Fresh token required')


@jwt.revoked_token_loader
def revoked_token_callback():
    return _error_handler(401, 'Token has been revoked')


@jwt.user_loader_error_loader
def user_loader_error_callback(identity):
    return _error_handler(401, "Error loading the user {}".format(identity))


@jwt.claims_verification_failed_loader
def verify_claims_failed_callback(identity):
    return _error_handler(401, "Error loading the user {}".format(identity))


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    return _error_handler(401, 'The {} token has expired'.format(expired_token['type']))


def _error_handler(code, message, **kwargs):
    return {'code': code, 'message': message, **kwargs}, code