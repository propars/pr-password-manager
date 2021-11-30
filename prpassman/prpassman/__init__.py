# http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
from .celery_app import app as celery_app

__all__ = ('celery_app',)