from . import ma
from marshmallow import validates_schema, ValidationError
from marshmallow.validate import Length, Email
from .models import User, Post, Comment


class UserSchema(ma.Schema):
    id = ma.String(dump_only=True)
    user_id = ma.String(load_only=True)
    first_name = ma.String(max_length=100, required=True, validate=Length(max=100))
    last_name = ma.String(max_length=100, required=True, validate=Length(max=100))
    email = ma.String(max_length=150, required=True, validate=[Email(), Length(max=150)])
    username = ma.String(max_length=50, required=True, validate=Length(max=50))
    phone = ma.String(max_length=30, required=True, validate=Length(max=30))

    class Meta:
        model = User
        additional = ("last_seen", "member_since", "password")
        dateformat = '%Y-%m-%dT%H:%M:%S%z'
        model_fields_kwargs = {'member_since': {'dump_only': True}, 'last_seen': {'dump_only': True},
                               'password': {'load_only': True}}

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("api.user_api", user_id="<id>"), "collection": ma.URLFor("api.user_api")}
    )

    @validates_schema
    def validate_unique_fields(self, data, **kwargs):
        errors = {}

        user = User.objects(email__iexact=data['email']).first() if data.get('user_id', None) is None else \
            User.objects(email__iexact=data['email'], id__ne=data['user_id']).first()
        if user is not None:
            errors['email'] = ["Email already exist."]
            print(user.id, data.get('id', None))

        user = User.objects(username__iexact=data['username']).first() if data.get('user_id', None) is None else \
            User.objects(username__iexact=data['username'], id__ne=data['user_id']).first()
        if user is not None:
            errors['username'] = ["Username already exist."]

        if errors:
            raise ValidationError(errors)


class CommentSchema(ma.Schema):
    id = ma.String(dump_only=True)
    body = ma.String(max_length=150000, required=True)
    disabled = ma.Boolean(default=False)
    timestamp = ma.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    author = ma.Nested(UserSchema)

    class Meta:
        model = Comment


class PostSchema(ma.Schema):
    id = ma.String(dump_only=True)
    image_url = ma.Url(required=True)
    title = ma.String(max_length=100, required=True)
    body = ma.String(max_length=150000, required=True)
    timestamp = ma.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    author = ma.Nested(UserSchema)

    class Meta:
        model = Post

    _links = ma.Hyperlinks(
        {"self": ma.URLFor("api.post_api", post_id="<id>"), "collection": ma.URLFor("api.post_api")}
    )


class FollowSchema(ma.Schema):
    id = ma.String(dump_only=True)
    timestamp = ma.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    follower = ma.Nested(UserSchema)