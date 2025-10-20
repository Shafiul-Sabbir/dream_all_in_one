from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings

def send_custom_email(subject, body, from_email, to, bcc=None, attachments=None, use_sales=False):
    """
    subject: str
    body: str (plain or html)
    from_email: str (e.g., sales@dreamziarah.com or noreply@dreamziarah.com)
    to: list of recipients
    bcc: optional list
    attachments: list of tuples (filename, content, mimetype)
    use_sales: bool -> True = sales SMTP config, False = default noreply
    """

    if use_sales:
        conf = settings.SALES_EMAIL_CONFIG
        connection = get_connection(
            host=conf["EMAIL_HOST"],
            port=conf["EMAIL_PORT"],
            username=conf["EMAIL_HOST_USER"],
            password=conf["EMAIL_HOST_PASSWORD"],
            use_tls=conf["EMAIL_USE_TLS"],
        )
    else:
        connection = get_connection()  # use default noreply config

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        bcc=bcc,
        connection=connection,
    )
    email.attach_alternative(body, "text/html")

    if attachments:
        for filename, content, mimetype in attachments:
            email.attach(filename, content, mimetype)

    email.send()
