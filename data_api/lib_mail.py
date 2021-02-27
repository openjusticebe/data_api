from smtplib import SMTP
from .lib_cfg import (config)
from .deps import (
    logger,
    jinjaEnv
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import namedtuple
import logging

Tpl = namedtuple('Tpl', ['file', 'subject', 'variables'])

TEMPLATE_CONFIG = {
    # User created new document
    'create_doc': Tpl(
        'mail_doc_create.html',
        'Notif: Nouveau document / Nieuw document',
        ['username', 'doc_hash', 'doc_domain']
    ),
    'publish_doc': Tpl(
        'mail_doc_publish.html',
        'Notif: Document publié / Document gepubliceerd',
        ['username', 'ecli', 'doc_domain']
    ),
}


def notify(user, templateName, data):
    try:
        tp = TEMPLATE_CONFIG[templateName]
        template = jinjaEnv.get_template(tp.file)
        body = template.render({
            **data,
            'username': user.username,
            'subject': tp.subject,
            'doc_domain': config.key('oj_doc_domain'),
        })
        send_mail(user.email, tp.subject, body)
        print("notification mail %s sent" % templateName)
        logger.info("notification mail %s sent", templateName)
    except Exception as e:
        logger.warning("Failed to send notification type %s to %s", templateName, user.username)
        logger.exception(e)


def send_mail(mTo, mSubject, mBody):
    mFrom = config.key(['smtp', 'user'])

    message = MIMEMultipart()
    message['Subject'] = mSubject
    message['From'] = "noreply@openjustice.be"
    message['To'] = mTo

    message.attach(MIMEText(mBody, "html"))
    msgBody = message.as_string()

    server = SMTP(config.key(['smtp', 'host']), config.key(['smtp', 'port']))
    server.starttls()
    server.login(mFrom, config.key(['smtp', 'password']))
    server.sendmail(mFrom, mTo, msgBody)

    server.quit()
