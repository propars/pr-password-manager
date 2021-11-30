
from django.utils import timezone
from celery import shared_task

from .models import Password


@shared_task
def check_expired_passwords():
    expired_qs = Password.objects.filter(is_alive=True, expire_date__lte=timezone.now())
    for passwd in expired_qs:
        passwd.is_alive = False
        passwd.save()

    # TODO mail atilacak
    # expired_non_archived_qs = Password.objects.filter(is_alive=False, is_archived=False)

