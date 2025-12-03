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
# Helper: Get company-specific SMTP connection
# ----------------------------
def get_company_email_connection(company_name):
    """
    Returns SMTP connection based on company name.
    In local mode, always returns local@dreamziarah.com
    In live mode, returns company-specific email
    """
    if IS_LOCAL:
        # Local এ সব email local@dreamziarah.com থেকে যাবে
        return get_connection(
            host="smtp.titan.email",
            port=587,
            username="local@dreamziarah.com",
            password=os.getenv("EMAIL_HOST_PASSWORD_FOR_LOCAL_DREAMZIARAH"),
            use_tls=True,
        )
    else:
        # Live এ company অনুযায়ী email যাবে
        config = settings.SALES_EMAIL_CONFIG.get(company_name)
        
        if not config:
            raise ValueError(f"No email configuration found for company: {company_name}")
        
        return get_connection(
            host=config["EMAIL_HOST"],
            port=config["EMAIL_PORT"],
            username=config["EMAIL_HOST_USER"],
            password=config["EMAIL_HOST_PASSWORD"],
            use_tls=config["EMAIL_USE_TLS"],
        )


def get_company_from_email(company_name):
    """
    Returns the from_email address based on company name and environment.
    """
    if IS_LOCAL:
        return "local@dreamziarah.com"
    else:
        email_map = {
            "IT": "sales@dreamtourism.it",
            "UK": "sales@dreamtourism.co.uk",
            "ZIARAH": "sales@dreamziarah.com"
        }
        return email_map.get(company_name,)


# ----------------------------
# 1. Welcome Email
# ----------------------------
def send_welcome_email_to_traveller(traveller_data):
    company = traveller_data.get('company')
    
    # Subject based on company
    subject_map = {
        "IT": "Account Confirmation - Dream IT SRLS.",
        "UK": "Account Confirmation - Dream UK SRLS.",
        "ZIARAH": "Account Confirmation - Dream Ziarah."
    }
    subject = subject_map.get(company,)
    
    # Get company-specific connection and from_email
    connection = get_company_email_connection(company)
    from_email = get_company_from_email(company)
    
    to = [traveller_data['email']]
    bcc = ["sabbirvai82@gmail.com"] if IS_LOCAL else []
    
    html_content = render_to_string(
        'payments/welcome_email_body_template.html',
        {"traveller_data": traveller_data}
    )
    
    email = EmailMultiAlternatives(
        subject, 
        html_content, 
        from_email, 
        to, 
        bcc=bcc, 
        connection=connection
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    print(f"✅ Welcome email sent from {from_email} to {traveller_data['email']}")


# ----------------------------
# 2. Booking Confirmation
# ----------------------------
def send_booking_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url):
    company = tour_booking.company.name
    print("company name : ", company)
    
    # Subject based on company
    subject_map = {
        "IT": f"Booking Confirmed - {tour_booking.tour.name} | Dream IT SRLS.",
        "UK": f"Booking Confirmed - {tour_booking.tour.name} | Dream UK SRLS.",
        "ZIARAH": f"Booking Confirmed - {tour_booking.tour.name} | Dream Ziarah"
    }
    subject = subject_map.get(company, f"Booking Confirmed - {tour_booking.tour.name} | Dream Tourism")
    
    # Get company-specific connection and from_email
    connection = get_company_email_connection(company)
    from_email = get_company_from_email(company)
    print("from email is : ", from_email)
    
    to = [traveller.user.email]
    bcc = ["sabbirvai82@gmail.com"] if IS_LOCAL else [
        "rakib.islam0000@gmail.com", 
        "mazumdermdashiq@gmail.com", 
        from_email
    ]
    
    context = {
        "tour_booking": tour_booking,
        "payment": payment,
        "traveller": traveller,
        "dashboard_url": dashboard_url,
    }
    
    html_content = render_to_string('payments/booking_confirmation_template.html', context)
    
    # Generate ticket PDF
    ticket_html = render_to_string('payments/tour_ticket.html', context)
    ticket_pdf_bytes = HTML(string=ticket_html).write_pdf(
        stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')]
    )
    pdf_filename = f"{tour_booking.tour.name}_Booking_Ticket.pdf"
    
    # Field-level update
    try:
        print("Updating booking ticket...")
        with transaction.atomic():
            tour_booking.refresh_from_db()
            tour_booking.booking_ticket.save(pdf_filename, ContentFile(ticket_pdf_bytes), save=False)
            tour_booking.save(update_fields=["booking_ticket"])
            print("Booking ticket updated successfully.")
    except Exception as e:
        print(f"❌ Error saving booking ticket PDF: {str(e)}")
    
    # Send email
    email = EmailMultiAlternatives(
        subject, 
        html_content, 
        from_email, 
        to, 
        bcc=bcc, 
        connection=connection
    )
    email.attach_alternative(html_content, "text/html")
    email.attach(pdf_filename, ticket_pdf_bytes, 'application/pdf')
    email.send()
    
    print(f"✅ Booking confirmation sent from {from_email} to {traveller.user.email}")


# ----------------------------
# 3. Payment Confirmation
# ----------------------------
def send_payment_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url):
    company = tour_booking.company.name
    
    # Subject based on company
    subject_map = {
        "IT": f"Payment Confirmed - {tour_booking.booking_id} | Dream IT SRLS.",
        "UK": f"Payment Confirmed - {tour_booking.booking_id} | Dream UK SRLS.",
        "ZIARAH": f"Payment Confirmed - {tour_booking.booking_id} | Dream Ziarah"
    }
    subject = subject_map.get(company, f"Payment Confirmed - {tour_booking.booking_id} | Dream Tourism")
    
    # Get company-specific connection and from_email
    connection = get_company_email_connection(company)
    from_email = get_company_from_email(company)
    
    to = [traveller.user.email]
    bcc = ["sabbirvai82@gmail.com"] if IS_LOCAL else [
        "rakib.islam0000@gmail.com", 
        "mazumdermdashiq@gmail.com",
        from_email
    ]
    
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
    invoice_pdf_bytes = HTML(string=invoice_html).write_pdf(
        stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')]
    )
    pdf_filename = f"{tour_booking.tour.name}_Payment_Invoice.pdf"
    
    # Generate invoice PDF without price 
    without_price_invoice_html = render_to_string('payments/payment_invoice_without_price.html', context)
    without_price_invoice_pdf_bytes = HTML(string=without_price_invoice_html).write_pdf(stylesheets=[CSS(string='@page { size: A4 landscape; margin: 10mm; }')])
    without_price_pdf_filename = f"{tour_booking.tour.name}_Payment_Invoice_Without_Price.pdf"
    
    # Field-level update
    try:
        print("updating booking payment_invoice & payment_invoice_without_price.")
        with transaction.atomic():
            tour_booking.refresh_from_db()
            tour_booking.payment_invoice.save(pdf_filename, ContentFile(invoice_pdf_bytes), save=False)
            tour_booking.payment_invoice_without_price.save(without_price_pdf_filename, ContentFile(without_price_invoice_pdf_bytes), save=False)
            tour_booking.save(update_fields=["payment_invoice", "payment_invoice_without_price"])  # শুধু payment_invoice আপডেট
            print("Payment invoice with & without price updated successfully.")
    except Exception as e:
        print(f"❌ Error saving payment invoice PDF: {str(e)}")
    
    # Send email
    email = EmailMultiAlternatives(
        subject, 
        html_content, 
        from_email, 
        to, 
        bcc=bcc, 
        connection=connection
    )
    email.attach_alternative(html_content, "text/html")
    email.attach(pdf_filename, invoice_pdf_bytes, 'application/pdf')
    email.attach(without_price_pdf_filename, without_price_invoice_pdf_bytes, 'application/pdf')
    email.send()
    
    print(f"✅ Payment confirmation sent from {from_email} to {traveller.user.email}")

