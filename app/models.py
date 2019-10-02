from . import mongo
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
from bson.objectid import ObjectId


class Follow(mongo.DynamicEmbeddedDocument):
    id = mongo.ObjectIdField(primary_key=True, default=ObjectId)
    timestamp = mongo.DateTimeField(default=datetime.utcnow())
    follower = mongo.ReferenceField('User')

    @staticmethod
    def find_follower_by_id(user_id=None, follower_id=None):
        if ObjectId.is_valid(user_id) and ObjectId.is_valid(follower_id):
            return User.objects(id=user_id, followers__match={"id": follower_id}).first_or_404()

        abort(404)


class Comment(mongo.DynamicEmbeddedDocument):
    id = mongo.ObjectIdField(primary_key=True, default=ObjectId)
    body = mongo.StringField()
    disabled = mongo.BooleanField(default=False)
    timestamp = mongo.DateTimeField(default=datetime.utcnow())
    author = mongo.ReferenceField('User')

    @staticmethod
    def find_comment_by_id(post_id=None, comment_id=None):
        if ObjectId.is_valid(post_id) and ObjectId.is_valid(comment_id):
            return Post.objects(id=post_id, comments__match={"id": comment_id}).first_or_404()

        abort(404)


class Post(mongo.DynamicDocument):
    image_url = mongo.StringField(default=None)
    title = mongo.StringField()
    body = mongo.StringField()
    timestamp = mongo.DateTimeField(default=datetime.utcnow())
    deleted_at = mongo.DateTimeField(default=None)
    author = mongo.ReferenceField('User')
    comments = mongo.EmbeddedDocumentListField('Comment')

    def is_author(self, author):
        return self.author == author

    @staticmethod
    def find_post_by_id(post_id=None):
        if ObjectId.is_valid(post_id):
            return Post.objects(id=post_id, deleted_at=None).first_or_404()

        abort(404)


class Role(mongo.DynamicEmbeddedDocument):
    name = mongo.StringField()
    default = mongo.BooleanField(default=False)
    permissions = mongo.IntField()

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        if self.permissions != 0:
            self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class User(mongo.DynamicDocument):
    username = mongo.StringField(unique=True)
    email = mongo.StringField(unique=True)
    enabled = mongo.BooleanField()
    first_name = mongo.StringField()
    last_name = mongo.StringField()
    birthday = mongo.DateTimeField()
    phone = mongo.StringField()
    about_me = mongo.StringField()
    address = mongo.StringField()
    member_since = mongo.DateTimeField(default=datetime.utcnow)
    last_seen = mongo.DateTimeField(default=datetime.utcnow)
    salt = mongo.StringField()
    hashed_password = mongo.StringField()
    confirmed = mongo.BooleanField(default=False)
    deleted_at = mongo.DateTimeField(default=None)
    roles = mongo.EmbeddedDocumentListField("Role")
    followings = mongo.EmbeddedDocumentListField("Follow")
    followers = mongo.EmbeddedDocumentListField("Follow")

    def is_following(self, follower):
        return self.followings.filter(follower=follower).first() is not None

    def is_followed(self, followed):
        return self.followers.filter(follower=followed).first() is not None

    def full_name(self):
        return "{first_name} {last_name}".format(first_name=self.first_name, last_name=self.last_name)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def can(self, perm):
        for role in self.roles:
            if role.has_permission(perm):
                return True
        return False

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()

    @staticmethod
    def find_user_by_id(user_id=None):
        if ObjectId.is_valid(user_id):
            return User.objects(id=user_id, deleted_at=None).first_or_404()

        abort(404)