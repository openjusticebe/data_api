from .lib_cfg import (config)
from .deps import (
    templates
)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import namedTuple

Tpl = namedTuple('Tpl', ['file', 'subject', 'variables'])

TEMPLATE_CONFIG = {
    # User created new document
    'create_doc': Tpl(
        'mail_doc_create.html',
        'Nouveau fichier / Nieuw document',
        ['username', 'doc_hash', 'doc_domain']
    )
}


def notify(user, templateName, data):
    try:
        tp = TEMPLATE_CONFIG[templateName])
        body = templates.templateResponse( tp.file, {
            **data,
            'username': user.name,
            'subject': tp.subject,
            'doc_domain': config.key('oj_doc_domain'),
        })
        send_mail(user.mail, tp.subject, body)
    except Exception as e:
        logger.warning("Failed to send notification type %s to $s", templateName, user.name)
        logger.exception(e)


def send_mail(mTo, mSubject, mBody):
    message = MIMEMultipart()
    message['Subject'] = mSubject
    message['From'] = config.key(['smtp' ,'user'])]
    message['To'] = mTo

    message.attach(MIMEText(mBody, "html"))
    msgBody = message.as_string()

    server = SMTP(config.key(['smtp', 'host']), config.key(['smtp', 'port']))
    server.starttls()
    server.login(mFrom, config.key(['smtp', 'password']))
    server.sendmail(mFrom, mTo, msgBody)

    server.quit()
