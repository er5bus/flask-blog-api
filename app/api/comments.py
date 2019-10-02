from . import api
from ..schemas import CommentSchema
from ..utils import get_current_user
from ..models import Post, Comment, Permission
from flask import request, abort
from flask.views import MethodView
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from ..decorators import permission_required_in
from bson import ObjectId


class CommentAPI(MethodView):
    decorators = [jwt_required]

    def __init__(self):
        self.comment_schema = CommentSchema()
        self.comment_schemas = CommentSchema(many=True)

    def get(self, post_id=None, comment_id=None):
        post = self.get_post(post_id)

        if comment_id is None:
            # return a list of comments
            page = request.args.get('page', type=int, default=1)
            item_per_page = request.args.get('item_per_page', type=int, default=10)
            offset = (page - 1) * item_per_page
            comments = post.comments[offset:offset + item_per_page]

            return dict(data=self.comment_schemas.dump(comments), has_more=len(comments) == item_per_page, code=200), 200
        else:
            # expose a single comment
            comment = Post.objects(id=post_id, comment__match={"id": comment_id}).first_or_404()
            return dict(data=self.comment_schema.dump(comment), code=200), 200

    @permission_required_in(Permission.COMMENT, Permission.MODERATE, Permission.ADMIN)
    def post(self, post_id=None):
        # create a new post
        try:
            post = self.get_post(post_id)
            data = self.comment_schema.load(request.json)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            comment = Comment(body=data['body'], author=get_current_user())
            post.comments.append(comment)
            post.comments.save()
            return dict(data=self.comment_schema.dump(comment), code=201), 201

    @permission_required_in(Permission.COMMENT, Permission.MODERATE, Permission.ADMIN)
    def put(self, post_id=None, comment_id=None):
        # update a single user
        try:
            comment = self.get_comment(post_id, comment_id)
            data = self.comment_schema.load(request.json, partial=True)
        except ValidationError as err:
            abort(400, err.messages)
        else:
            Post.objects(comments__id=comment_id).update_one(
                set__comments__S__body=data.get('body', comment.body),
                set__comments__S__disabled=data.get('disabled',
                                                    comment.disabled))
            return dict(data=self.comment_schema.dump(self.get_comment(post_id, comment_id)), code=200), 200

    @permission_required_in(Permission.COMMENT, Permission.MODERATE, Permission.ADMIN)
    def delete(self, post_id=None, comment_id=None):
        # delete a single user
        comment = self.get_comment(post_id, comment_id)
        Post.objects(comments__id=comment_id).update_one(pull__comments=comment)
        return dict(code=204), 204

    def get_comment(self, post_id, comment_id):
        if not ObjectId.is_valid(post_id) or not ObjectId.is_valid(comment_id): abort(404)
        comment = self.get_post(post_id).comments.filter(id=comment_id).first()
        if comment is None: abort(404)
        return comment

    @staticmethod
    def get_post(post_id):
        if not ObjectId.is_valid(post_id): abort(404)
        return Post.objects(id=post_id).first_or_404()


comment_view = CommentAPI.as_view('post_comment_api')
api.add_url_rule('/posts/<string:post_id>/comments', view_func=comment_view, methods=['GET', 'POST'])
api.add_url_rule('/posts/<string:post_id>/comments/<string:comment_id>', view_func=comment_view, methods=['GET', 'PUT', 'DELETE'])