#!/usr/bin/env python

from wtforms import Form, HiddenField, StringField, PasswordField, validators, BooleanField

class AddShop(Form):
    name = StringField('Name', [validators.length(min=1, max=255)])
    url = StringField('URL', [validators.DataRequired()])
    active = BooleanField('Active')

    secret = StringField('Shopify API Secret', [validators.DataRequired()])
    password = StringField('Shopify API Password', [validators.DataRequired()])

class EditShop(AddShop):
    id = HiddenField('id', [validators.DataRequired()])
