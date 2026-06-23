from django.core.signing import TimestampSigner
import os
import django
from django.conf import settings

settings.configure(SECRET_KEY='django-insecure-local-dev-key-change-me')
django.setup()

signer = TimestampSigner()
signed = signer.sign('E7DMYB')
print('SIGNED:', signed)
print('UNSIGNED:', signer.unsign(signed, max_age=20))
