#!/usr/bin/env python
import os

class ConfigClass(object):
    # Flask Settings
    SECRET_KEY                     = os.getenv('SECRET_KEY', '0574511B-546E-0C35-BD4C-E2A64D26DB35')
    SQLALCHEMY_DATABASE_URI        = os.getenv('DATABASE_URL', 'mysql+mysqldb://onecollect:0n3l1v3M3d14@localhost/olm?charset=utf8')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CSRF_ENABLED                   = True

    # Flask-Mail Settings
    MAIL_USERNAME                  = os.getenv('MAIL_USERNAME', 'onecollective')
    MAIL_PASSWORD                  = os.getenv('MAIL_PASSWORD', 'sxvtZ5Ks')
    MAIL_DEFAULT_SENDER            = os.getenv('MAIL_DEFAULT_SENDER', '"OneCollectLive" <steve.gricci@onelivemedia.com>')
    MAIL_SERVER                    = os.getenv('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT                      = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USE_SSL                   = int(os.getenv('MAIL_USE_SSL', True))

    # Flask-User Settings
    USER_APP_NAME                  = "OneCollectLive"
