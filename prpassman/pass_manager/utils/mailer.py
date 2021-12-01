
import time
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.utils import formataddr
from email.header import Header
import smtplib

from django.core.validators import validate_email
from django.conf import settings


FROM_ADDRES = settings.EMAIL_FROM_ADDRESS
NOREPLY = settings.EMAIL_NOREPLY_ADDRESS


def send_mail__smtp(to_address, subject, mail_body, mime_type='plain', attachments=None, from_name=None):
    if isinstance(to_address, str):
        to_address = (to_address,)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = formataddr((str(Header(from_name, 'utf-8')), FROM_ADDRES))
    msg['To'] = ",".join(list(to_address))
    msg["Date"] = str(formatdate())
    msg["Reply-To"] = NOREPLY
    msg.attach(MIMEText(mail_body, _subtype=mime_type, _charset="utf-8"))

    if attachments is not None:
        for attachment in attachments:
            msg.attach(attachment)

    server = smtplib.SMTP(str(settings.MAILSERVICE_SMTP_HOST), str(settings.MAILSERVICE_SMTP_PORT))

    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(str(settings.MAILSERVICE_SMTP_USER), str(settings.MAILSERVICE_SMTP_PASS))
    server.sendmail(FROM_ADDRES, to_address, msg.as_string())
    server.quit()

    return True


def timeout_safe_post(*args, **kwargs):
    retry_left = kwargs.pop('retry_left', 5)    # varsayilan 5 deneme
    kwargs['timeout'] = (5, 15)     # 5 saniye baglanma, 15 saniye cevap okuma
    try:
        return requests.post(*args, **kwargs)
        # TODO ReadTimeout alinirsa aslinda mail gitmis de olabilir, ortak degisken bulunup kontrol edilecek
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
        retry_left -= 1
        if retry_left < 0:
            raise
        else:
            time.sleep(.5)
            return timeout_safe_post(*args, retry_left=retry_left, **kwargs)


def send_mail__mailgun_api(to_address, subject, mail_body, mime_type='plain', attachments=None, from_name=None):
    try:
        validate_email(to_address)
    except:
        raise Exception('INVALID_EMAIL')

    _from = '{} <{}>'.format(from_name, FROM_ADDRES) if from_name else '<{}>'.format(FROM_ADDRES)
    resp = timeout_safe_post(
        "https://api.mailgun.net/v3/{}/messages".format(settings.MG_DOMAIN),
        auth=("api", settings.MG_API_KEY),
        data={"from": _from,
              "to": to_address,
              "subject": subject,
              'html' if mime_type == 'html' else 'text': mail_body,
              'h:Reply-To': NOREPLY
              })
    if resp.ok:
        resp_json = resp.json()
        if 'id' in resp_json:
            return True
        else:
            raise Exception(str(resp_json))
    else:
        if resp.status_code == 400:
            raise Exception(' | '.join((str(resp.url), str(resp.reason), str(resp.json()))))
        resp.raise_for_status()


send_mail = send_mail__smtp     #send_mail__mailgun_api
