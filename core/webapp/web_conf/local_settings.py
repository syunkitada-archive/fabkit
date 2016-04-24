# coding: utf-8

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fabkit_web',
        'USER': 'fabkit',
        'PASSWORD': 'fabkitpass',
        'HOST': '192.168.122.55',
        'PORT': '3306',
    }
}
