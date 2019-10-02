from flask import request
from . import api
from ..models import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
from flask.views import MethodView


class UserLoginAPI(MethodView):

    def post(self):
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        current_user = User.objects(username=username).first() if password and username else None
        if current_user is not None and current_user.check_password(password):
            return dict(code=200, access_token=create_access_token(identity=str(current_user.id)),
                        refresh_token=create_refresh_token(identity=str(current_user.id))), 200

        return dict(code=200, message='Invalid username or password.'), 200


class TokenRefreshAPI(MethodView):

    @jwt_refresh_token_required
    def post(self):
        return dict(code=200, access_token=create_access_token(identity=get_jwt_identity())), 200


user_login_view = UserLoginAPI.as_view('user_login_api')
api.add_url_rule('/login', view_func=user_login_view, methods=['POST'])

token_refresh_view = TokenRefreshAPI.as_view('token_refresh_api')
api.add_url_rule('/token/refresh', view_func=token_refresh_view, methods=['POST'])
