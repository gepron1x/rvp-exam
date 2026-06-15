from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user, login_required

from app.models import User

USER = "Пользователь"
MODERATOR = "Модератор"
ADMIN = "Администратор"

roles = [USER, MODERATOR, ADMIN]


def has_role_or_higher(user: User, role: str) -> bool:
    idx = roles.index(role)
    if idx == -1:
        return False
    return roles.index(user.role.name) >= idx

def check_role(role: str):
    if not current_user.is_authenticated:
        return False
    return has_role_or_higher(current_user, role)

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):

            if has_role_or_higher(current_user, required_role):
                return f(*args, **kwargs)
            flash("У вас недостаточно прав для выполнения данного действия.", "danger")
            return redirect(url_for('main.index'))
        return decorated_function
    return decorator
