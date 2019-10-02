from . import api
from ..models import User, Follow
from ..schemas import FollowSchema
from flask_jwt_extended import jwt_required
from flask.views import MethodView
from flask import request, abort
from bson import ObjectId


class FollowersAPI(MethodView):
    decorators = [jwt_required]

    def __init__(self):
        self.follow_schema = FollowSchema()
        self.follow_schemas = FollowSchema(many=True)

    def get(self, user_id=None, follower_id=None):
        if follower_id is None:
            page = request.args.get('page', type=int, default=1)
            item_per_page = request.args.get('item_per_page', type=int, default=10)
            offset = (page - 1) * item_per_page
            followers = User.find_user_by_id(user_id).followers[offset:offset + item_per_page]
            return dict(data=self.follow_schemas.dump(followers), has_more=len(followers) == item_per_page, code=200), 200
        else:
            follower = Follow.find_follower_by_id(user_id, follower_id)
            return dict(data=self.follow_schema.dump(follower), code=200), 200

    @staticmethod
    def get_follower(user_id=None, follower_id=None):
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(follower_id): abort(404)
        return User.objects(id=user_id, followers__match={"id": follower_id}).first_or_404()


class FollowingsAPI(MethodView):
    decorators = [jwt_required]

    def __init__(self):
        self.follow_schema = FollowSchema()
        self.follow_schemas = FollowSchema(many=True)

    def get(self, user_id=None, follower_id=None):
        if follower_id is None:
            page = request.args.get('page', type=int, default=1)
            item_per_page = request.args.get('item_per_page', type=int, default=10)
            offset = (page - 1) * item_per_page
            followings = User.find_user_by_id(user_id).followings[offset:offset + item_per_page]
            return dict(data=self.follow_schemas.dump(followings), has_more=len(followings) == item_per_page, code=200), 200
        else:
            follower = Follow.find_follower_by_id(user_id, follower_id)
            return dict(data=self.follow_schema.dump(follower), code=200), 200

    @staticmethod
    def get_follower(user_id=None, follower_id=None):
        if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(follower_id): abort(404)
        return User.objects(id=user_id, followers__match={"id": follower_id}).first_or_404()


class FollowAPI(MethodView):
    decorators = [jwt_required]

    def post(self, user_id, user_to_follow_id):
        user = User.find_user_by_id(user_id)
        user_to_follow = User.find_user_by_id(user_to_follow_id)

        if user.is_followed(user_to_follow) and user_to_follow.is_following(user):
            return dict(code=200, message='You are already following %s.' % user.username), 200

        user_to_follow.followings.append(Follow(follower=user))
        user_to_follow.followings.save()

        user.followers.append(Follow(follower=user_to_follow))
        user.followers.save()

        return dict(code=200, message='You are now following %s.' % user.username), 200


class UnFollowAPI(MethodView):
    decorators = [jwt_required]

    def post(self, user_id, user_to_follow_id):
        user = User.find_user_by_id(user_id)
        user_to_follow = User.find_user_by_id(user_to_follow_id)

        if not user.is_followed(user_to_follow) and not user_to_follow.is_following(user):
            return dict(code=200, message='You are already not following %s.' % user.username), 200

        user_follower = user.followers.filter(follower=user_to_follow).first()
        follower_follower = user_to_follow.followings.filter(follower=user).first()

        User.objects(id=user_id).update_one(pull__followers=user_follower)
        User.objects(id=user_to_follow_id).update_one(pull__followings=follower_follower)
        return dict(code=200, message='You are now not following %s.' % user.username), 200


followers_view = FollowersAPI.as_view('followers_api')
api.add_url_rule('/users/<string:user_id>/followers', view_func=followers_view, methods=['GET'])
api.add_url_rule('/users/<string:user_id>/followers/<string:follower_id>', view_func=followers_view, methods=['GET'])

followings_view = FollowingsAPI.as_view('followings_api')
api.add_url_rule('/users/<string:user_id>/followings', view_func=followings_view, methods=['GET'])
api.add_url_rule('/users/<string:user_id>/followings/<string:follower_id>', view_func=followings_view, methods=['GET'])

follow_view = FollowAPI.as_view('follow_api')
api.add_url_rule('/users/<string:user_id>/follow/<string:follower_id>', view_func=follow_view, methods=['POST'])

unfollow_view = UnFollowAPI.as_view('unfollow_api')
api.add_url_rule('/users/<string:user_id>/unfollow/<string:follower_id>', view_func=unfollow_view, methods=['POST'])