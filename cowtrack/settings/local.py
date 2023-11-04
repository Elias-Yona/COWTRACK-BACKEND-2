from . base import *


if DEBUG:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    ]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025
