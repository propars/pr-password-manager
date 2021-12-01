
from django.utils import timezone
from django.conf import settings
from celery import shared_task

from .models import Password

from .utils.mailer import send_mail


@shared_task
def check_expired_passwords():
    expired_qs = Password.objects.filter(is_alive=True, expire_date__lte=timezone.now())
    for passwd in expired_qs:
        passwd.is_alive = False
        passwd.save()

    three_days_later = timezone.now() + timezone.timedelta(days=3)
    expired_non_archived_qs = Password.objects.filter(is_archived=False, expire_date__lte=three_days_later)
    if expired_non_archived_qs.exists():
        title = 'Propars Password Manager - Expiring password(s) found'
        body = ''
        for expired_pw in expired_non_archived_qs:
            body += '{} -- {} -- {} {}\n'.format(expired_pw.pk, expired_pw.name, expired_pw.expire_date,
                                                 '-- EXPIRED' if expired_pw.expire_date <= timezone.now() else '')
        send_mail(to_address=settings.EXPIRED_ALERT_RECEIVER_EMAILS, subject=title,  mail_body=body)

