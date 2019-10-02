from . import api
from flask_jwt_extended import jwt_required
from ..models import Post, Permission
from ..schemas import PostSchema
from ..decorators import permission_required_in
from ..utils import get_current_user
from flask.views import MethodView
from flask import request, abort, g
from marshmallow import ValidationError
from datetime import datetime


class PostAPI(MethodView):
    decorators = [jwt_required]

    def __init__(self):
        self.post_schemas = PostSchema(many=True)
        self.post_schema = PostSchema()

    def get(self, post_id=None):
        """List all posts"""
        if post_id is None:
            # return a list of posts
            page = request.args.get('page', type=int, default=1)
            item_per_page = request.args.get('item_per_page', type=int, default=10)
            paginator = Post.objects(delete_at=None).paginate(page, per_page=item_per_page)
            return dict(data=self.post_schemas.dump(paginator.items), has_more=paginator.pages > page, code=200), 200
        else:
            # expose a single post
            post = Post.find_post_by_id(post_id)
            return dict(data=self.post_schema.dump(post), code=200), 200

    @permission_required_in(Permission.WRITE, Permission.MODERATE, Permission.ADMIN)
    def post(self):
        # create a new post
        try:
            data = self.post_schema.load(request.json)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            post = Post(image_url=data['image_url'], title=data['title'], body=data['body'], author=get_current_user())
            post.save(force_insert=True)
            return dict(data=self.post_schema.dump(post), code=201), 201

    @permission_required_in(Permission.WRITE, Permission.MODERATE, Permission.ADMIN)
    def put(self, post_id):
        # update a single post
        try:
            post = Post.find_post_by_id(post_id)
            data = self.post_schema.load(request.json, partial=True, unknown=True)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            post.update(set__image_url=data.get('image_url', post.image_url), set__title=data.get('title', post.title), set__body=data.get('body', post.body))
            post.reload()
            return dict(data=self.post_schema.dump(post), code=200), 200

    @permission_required_in(Permission.WRITE, Permission.MODERATE, Permission.ADMIN)
    def delete(self, post_id):
        # delete a single post
        post = Post.find_post_by_id(post_id)
        post.update(set__delete_at=datetime.utcnow())
        return dict(data=self.post_schema.dump(post), code=204), 204


post_view = PostAPI.as_view('post_api')
api.add_url_rule('/posts/', view_func=post_view, methods=['GET', 'POST'])
api.add_url_rule('/posts/<string:post_id>', view_func=post_view, methods=['GET', 'PUT', 'DELETE'])
