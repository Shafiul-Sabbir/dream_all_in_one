# tours/emails.py

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
# 1. Date Change Request To Admin (sales SMTP)
# ----------------------------
def send_date_change_request_email_to_admin(tour_booking, admin_all_booking_page_url):
    subject = f"Request To Change Date of Booking - {tour_booking.booking_id}"
    
    if IS_LOCAL:
        to = ["local@dreamziarah.com"]
        bcc = ["sabbirvai82@gmail.com", "local@dreamziarah.com"]
    else:
        to = ["sales@dreamziarah.com"]
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "admin_all_booking_page_url" : admin_all_booking_page_url
    }

    html_content = render_to_string('tour/date_change_request_template.html', context)

    # Send via sales SMTP
    connection = get_sales_connection()
    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Date Change Request sent from sales to sales")


# ----------------------------
# 2. Date Change Request Approve (sales SMTP)
# ----------------------------
def send_date_change_request_approval_email_from_admin_to_traveller(tour_booking, traveller_dashboard_url):
    subject = f"Date Change Request Approved for Booking - {tour_booking.booking_id}"
    to = [tour_booking.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "traveller_dashboard_url": traveller_dashboard_url
    }

    html_content = render_to_string('tour/date_change_request_approval_template.html', context)

    # Generate ticket PDF
    changed_ticket_html = render_to_string('tour/date_change_request_approval_tour_ticket_template.html', context)
    ticket_pdf_bytes = HTML(string=changed_ticket_html).write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')])
    pdf_filename = f"{tour_booking.tour.name}_Changed_Date's_Booking_Ticket.pdf"

    # ✅ Field-level update (no overwrite of payment_invoice)
    try:
        print("updating changed date's booking ticket.")
        with transaction.atomic():
            tour_booking.refresh_from_db()  # latest data নাও
            tour_booking.booking_ticket.save(pdf_filename, ContentFile(ticket_pdf_bytes), save=False)
            tour_booking.save(update_fields=["booking_ticket"])  # শুধু booking_ticket আপডেট
            print("booking ticket updated successfully because of changing date.")

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
    print("✅ Changed date's Booking confirmation sent from sales to", tour_booking.user.email)


# ----------------------------
# 3. Date Change Request Deny (sales SMTP)
# ----------------------------
def send_date_change_request_deny_email_to_traveller(tour_booking, requested_selected_date, traveller_dashboard_url):
    subject = f"Date Change Request Denied for Booking - {tour_booking.booking_id}"
    to = [tour_booking.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "requested_selected_date": requested_selected_date,
        "traveller_dashboard_url": traveller_dashboard_url,
    }

    html_content = render_to_string('tour/date_change_request_deny_template.html', context)

    # Send via sales SMTP
    connection = get_sales_connection()

    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    print("from email : ", from_email)
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Booking date change request denied email sent from sales to", tour_booking.user.email)



# ----------------------------
# 4. Booking Cancellation Request To Admin (sales SMTP)
# ----------------------------
def send_booking_cancellation_request_email_to_admin(tour_booking, admin_all_booking_page_url):
    subject = f"Request To Cancel Booking - {tour_booking.booking_id}"
    
    if IS_LOCAL:
        to = ["local@dreamziarah.com"]
        bcc = ["local@dreamziarah.com"]
    else:
        to = ["sales@dreamziarah.com"]
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "admin_all_booking_page_url" : admin_all_booking_page_url
    }

    html_content = render_to_string('tour/booking_cancellation_request_template.html', context)

    # Send via sales SMTP
    connection = get_sales_connection()
    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Booking Cancellation Request sent from sales to sales")



# ----------------------------
# 5. Booking Cancellation Request approval (sales SMTP)
# ----------------------------
def booking_cancellation_request_approval_email_from_admin_to_traveller(tour_booking, traveller_dashboard_url):
    subject = f"Booking Cancellation Request Approved for Booking - {tour_booking.booking_id}"
    to = [tour_booking.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "traveller_dashboard_url": traveller_dashboard_url
    }

    html_content = render_to_string('tour/booking_cancellation_request_approval_template.html', context)

    # Send via sales SMTP
    connection = get_sales_connection()

    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    print("from email : ", from_email)
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Booking cancellation Request approval email sent from sales to", tour_booking.user.email)

# ----------------------------
# 6. Booking Cancellation Request Deny (sales SMTP)
# ----------------------------
def send_booking_cancellation_request_deny_email_to_traveller(tour_booking, traveller_dashboard_url):
    subject = f"Booking Cancellation Request Denied for Booking - {tour_booking.booking_id}"
    to = [tour_booking.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "traveller_dashboard_url": traveller_dashboard_url,
    }

    html_content = render_to_string('tour/booking_cancellation_request_deny_template.html', context)

    # Send via sales SMTP
    connection = get_sales_connection()

    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    print("from email : ", from_email)
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Booking cancellation request denied email sent from sales to", tour_booking.user.email)


# ----------------------------
# 7. Manual Cancellation of Booking by Admin (sales SMTP)
# ----------------------------
def send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin(tour_booking, traveller_dashboard_url):
    subject = f"Booking Manually Cancelled by Admin - {tour_booking.booking_id}"
    to = [tour_booking.user.email]
    if IS_LOCAL:
        bcc = ["sabbirvai82@gmail.com"]
    else:
        bcc = ["dreamziarah@gmail.com", "rakib.islam0000@gmail.com", "mazumdermdashiq@gmail.com", "sales@dreamziarah.com"]

    context = {
        "tour_booking": tour_booking,
        "traveller_dashboard_url": traveller_dashboard_url,
    }
    html_content = render_to_string('tour/manual_cancellation_of_booking_by_admin_template.html', context)
    # Send via sales SMTP
    connection = get_sales_connection()
    from_email = settings.SALES_FROM_EMAIL   # must match sales SMTP user
    print("from email : ", from_email)
    email = EmailMultiAlternatives(subject, html_content, from_email, to, bcc=bcc, connection=connection)
    email.attach_alternative(html_content, "text/html")
    email.send()
    print("✅ Manual cancellation of booking by admin email sent from sales to", tour_booking.user.email)