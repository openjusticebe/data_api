from collections import namedtuple
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from .deps import jinjaEnv, logger, oj_db
from .lib_cfg import config
from .lib_parse import latex2pdf, md2latex

Tpl = namedtuple('Tpl', ['file', 'subject', 'variables', 'attach_pdf'])
OJ_ENV = config.key('oj_env')

TEMPLATE_CONFIG = {
    # User created new document
    'create_doc': Tpl(
        'mail_doc_create.html',
        'Notif: Nouveau document / Nieuw document',
        ['username', 'doc_hash', 'doc_domain'],
        True
    ),
    'publish_doc': Tpl(
        'mail_doc_publish.html',
        'Notif: Document publié / Document gepubliceerd',
        ['username', 'ecli', 'doc_domain'],
        False
    ),
}


async def notify(user, templateName, data):
    try:
        tp = TEMPLATE_CONFIG[templateName]
        template = jinjaEnv.get_template(tp.file)
        body = template.render({
            **data,
            'username': user.username,
            'subject': tp.subject,
            'doc_domain': config.key('oj_doc_domain'),
        })
        subject = tp.subject if OJ_ENV == 'prod' else f"[{OJ_ENV}] {tp.subject}"

        attachments = await get_attachments('ecli', {'dochash': data['doc_hash']}) if tp.attach_pdf else []

        send_mail(user.email, subject, body, attachments)
        logger.info("notification mail \'%s\' sent", subject)
    except Exception as e:
        logger.warning("Failed to send notification type %s to %s", templateName, user.username)
        logger.exception(e)


async def get_attachments(kind, data):
    if kind != 'ecli':
        return []

    dochash = data['dochash']
    sql = """
    SELECT court, year, ecli, text
    FROM ecli_document
    WHERE hash = $1
    """

    async with oj_db() as db:
        res = await db.fetchrow(sql, dochash)

    latex = md2latex({
        'body': res['text'],
        'title': res['ecli'],
    })
    now = datetime.now()
    fname = "{court}_{year}_OJ_v{date}.pdf".format(
        court=res['court'],
        year=res['year'],
        date=now.strftime("%d%m%Y")
    )

    part = MIMEApplication(
        latex2pdf(latex),
        Name=fname
    )
    part['Content-Disposition'] = f'attachment; filename="{fname}"'

    logger.debug('Attaching file %s', fname)
    return [
        part
    ]


def send_mail(mTo, mSubject, mBody, mAttach):
    mFrom = config.key(['smtp', 'user'])

    message = MIMEMultipart()
    message['Subject'] = mSubject
    message['From'] = "noreply@openjustice.be"
    message['To'] = mTo

    message.attach(MIMEText(mBody, "html"))

    [message.attach(m) for m in mAttach]

    msgBody = message.as_string()

    try:
        server = SMTP(host=config.key(['smtp', 'host']), port=config.key(['smtp', 'port']), timeout=5)
        # Server is now internal, TLS not used anymore
        # server.starttls()
        # server.login(mFrom, config.key(['smtp', 'password']))
        server.sendmail(mFrom, mTo, msgBody)
        server.quit()
    except Exception as e:
        logger.critical("Failed to send a message")
        logger.exception(e)
