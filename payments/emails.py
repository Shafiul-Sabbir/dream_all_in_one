# payments/emails.py

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from weasyprint import HTML, CSS
from payments.models import Payment
from tour.models import TourBooking
from django.db import transaction
import os 

IS_LOCAL = os.environ.get("IS_LOCAL", "False").strip().lower() == "true"

# ----------------------------
# Helper: get sales SMTP connection
# ----------------------------
def get_sales_connection():
    conf = settings.SALES_EMAIL_CONFIG
    return get_connection(
        host=conf["EMAIL_HOST"],
        port=conf["EMAIL_PORT"],
        username=conf["EMAIL_HOST_USER"],
        password=conf["EMAIL_HOST_PASSWORD"],
        use_tls=conf["EMAIL_USE_TLS"],
    )

# ----------------------------
# 1. Welcome Email (default noreply SMTP)
# ----------------------------
def send_welcome_email_to_traveller(traveller_data):
    subject = "Account Confirmation - DreamZiarah"
    from_email = settings.DEFAULT_FROM_EMAIL   # noreply
    to = [traveller_data['email']]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = []

    html_content = render_to_string(
        'payments/welcome_email_body_template.html',
        {"traveller_data": traveller_data}
    )

    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Welcome email sent from noreply to", traveller_data['email'])


# ----------------------------
# 2. Booking Confirmation (sales SMTP)
# ----------------------------
def send_booking_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url):
    subject = f"Booking Confirmed - {tour_booking.tour.name} | DreamZiarah"
    to = [traveller.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "payment": payment,
        "traveller": traveller,
        "dashboard_url": dashboard_url,
    }

    html_content = render_to_string('payments/booking_confirmation_template.html', context)

    # Generate ticket PDF
    ticket_html = render_to_string('payments/tour_ticket.html', context)
    ticket_pdf_bytes = HTML(string=ticket_html).write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')])
    pdf_filename = f"{tour_booking.tour.name}_Booking_Ticket.pdf"

    # ✅ Field-level update (no overwrite of payment_invoice)
    try:
        print("updating booking ticket.")
        with transaction.atomic():
            tour_booking.refresh_from_db()  # latest data নাও
            tour_booking.booking_ticket.save(pdf_filename, ContentFile(ticket_pdf_bytes), save=False)
            tour_booking.save(update_fields=["booking_ticket"])  # শুধু booking_ticket আপডেট
            print("booking ticket updated successfully.")

    except Exception as e:
        print("❌ Error saving booking ticket PDF:", str(e))

    # Send via sales SMTP
    connection = get_sales_connection()

    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    print("from email : ", from_email)
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.attach(pdf_filename, ticket_pdf_bytes, 'application/pdf')
    email.send()
    print("✅ Booking confirmation sent from sales to", traveller.user.email)


# ----------------------------
# 3. Payment Confirmation (sales SMTP)
# ----------------------------
def send_payment_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url):
    subject = f"Payment Confirmed - {tour_booking.booking_id} | DreamZiarah"
    # from_email = settings.SALES_EMAIL_CONFIG["EMAIL_HOST_USER"]   # sales
    to = [traveller.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "payment": payment,
        "traveller": traveller,
        "dashboard_url": dashboard_url,
        "now": timezone.now(),
    }

    html_content = render_to_string('payments/payment_confirmation_template.html', context)

    # Generate invoice PDF
    invoice_html = render_to_string('payments/payment_invoice.html', context)
    invoice_pdf_bytes = HTML(string=invoice_html).write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')])
    pdf_filename = f"{tour_booking.tour.name}_Payment_Invoice.pdf"

    # ✅ Field-level update (no overwrite of booking_ticket)
    try:
        print("updating booking payment_invoice.")
        with transaction.atomic():
            tour_booking.refresh_from_db()  # latest data নাও
            tour_booking.payment_invoice.save(pdf_filename, ContentFile(invoice_pdf_bytes), save=False)
            tour_booking.save(update_fields=["payment_invoice"])  # শুধু payment_invoice আপডেট
            print("booking payment invoice updated successfully.")

    except Exception as e:
        print("❌ Error saving payment invoice PDF:", str(e))

    # Send via sales SMTP
    connection = get_sales_connection()
    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.attach(pdf_filename, invoice_pdf_bytes, 'application/pdf')
    email.send()
    print("✅ Payment confirmation sent from sales to", traveller.user.email)

