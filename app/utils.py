from flask_jwt_extended import get_jwt_identity
from .models import User


def has_permissions(user, *perms):
    for perm in perms:
        if user.can(perm):
            return True
    return False


def get_current_user():
    return User.objects(id=get_jwt_identity(), delete_at=None).first() if get_jwt_identity() is not None else None