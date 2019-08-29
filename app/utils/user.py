#!/usr/bin/env python
from app import login_manager
from flask import redirect, url_for
from flask.ext.login import UserMixin
from app.models import User as dbUser
import hashlib

class User(UserMixin):
    id               = None
    email            = None
    active           = None
    first_name       = None
    last_name        = None
    is_authenticated = False
    is_active        = False
    is_anonymous     = False

    def __init__(self, user_record):
        self.id = user_record.id
        self.email = user_record.email
        self.active = user_record.active
        self.first_name = user_record.first_name
        self.last_name = user_record.last_name
        self.is_authenticated = True
        if self.active:
            self.is_active = True

    def get_id(self):
        return self.id


@login_manager.user_loader
def user_loader(user_id):
    user_record = dbUser.get(user_id)
    user = User(user_record)
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if not email or not dbUser.exists_by_email(email):
        return

    user_record = dbUser.authenticate(email, request.form['password'])
    if not user_record:
        return None

    user = User(user_record)
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))
