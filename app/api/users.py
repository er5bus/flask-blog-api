from . import api
from ..models import User, Permission
from ..schemas import UserSchema
from ..decorators import permission_required_eq
from flask.views import MethodView
from flask import request, abort
from marshmallow import ValidationError
from datetime import datetime


class UserAPI(MethodView):

    def __init__(self):
        self.user_schemas = UserSchema(many=True)
        self.user_schema = UserSchema()

    @permission_required_eq(Permission.ADMIN)
    def get(self, user_id=None):
        """List all users"""
        if user_id is None:
            # return a list of users
            page = request.args.get('page', type=int, default=1)
            item_per_page = request.args.get('item_per_page', type=int, default=10)
            paginator = User.objects(deleted_at=None).paginate(page, per_page=item_per_page)
            return dict(code=200, data=self.user_schemas.dump(paginator.items), has_more=paginator.pages > page), 200
        else:
            # expose a single user
            user = User.find_user_by_id(user_id)
            return dict(data=self.user_schema.dump(user), code=200), 200

    def post(self):
        # create a new user
        try:
            data = self.user_schema.load(request.json)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            user = User(first_name=data['first_name'], last_name=data['last_name'], phone=data['phone'],
                        email=data['email'], username=data['username'])
            user.password = data['password']
            user.save(force_insert=True)
            return dict(data=self.user_schema.dump(user), code=201), 201

    @permission_required_eq(Permission.ADMIN)
    def put(self, user_id):
        # update a single user
        try:
            user = User.find_user_by_id(user_id)
            data = self.user_schema.load({**request.json, 'user_id': str(user.id)}, partial=True, unknown=True)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            if 'password' in data: user.password = data['password']
            user.update(set__first_name=data.get('first_name', user.first_name), set__last_name=data.get('last_name', user.last_name), set__phone=data.get('phone', user.phone),
                        set__email=data.get('email', user.email), set__username=data.get('username', user.username), set__hashed_password=user.hashed_password)
            user.reload()
            return dict(code=200, data=self.user_schema.dump(user)), 200

    @permission_required_eq(Permission.ADMIN)
    def delete(self, user_id):
        # delete a single user
        user = User.find_user_by_id(user_id)
        user.update(set__delete_at=datetime.utcnow())
        return dict(code=204)


user_view = UserAPI.as_view('user_api')
api.add_url_rule('/users/', view_func=user_view, methods=['GET', 'POST'])
api.add_url_rule('/users/<string:user_id>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])
