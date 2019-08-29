#!/usr/bin/env python

from wtforms import Form, StringField, PasswordField, HiddenField, BooleanField, validators

class AddUser(Form):
    email = StringField('Email', [validators.length(min=6, max=35)])
    first_name = StringField('First Name', [validators.length(min=1, max=35)])
    last_name = StringField('Last Name', [validators.length(min=1, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class EditUser(Form):
    id = HiddenField('id', [validators.DataRequired()])
    email = StringField('Email', [validators.length(min=6, max=35)])
    first_name = StringField('First Name', [validators.length(min=1, max=35)])
    last_name = StringField('Last Name', [validators.length(min=1, max=35)])
    active = BooleanField('Active')

class ChangePassword(Form):
    id = HiddenField('id', [validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
