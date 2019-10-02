from functools import wraps
from .utils import get_current_user, has_permissions
from flask import abort


def permission_required_in(*perms):
    def check_permission(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if user is None or not has_permissions(user, *perms):
                abort(401, 'You do not have sufficient permissions to access this page.')
            return func(*args, **kwargs)
        return wrapped
    return check_permission


def permission_required_eq(perm):
    return permission_required_in(perm)