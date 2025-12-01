from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from payments.models import Payment, Traveller
from tour.models import TourBooking
import os
from time import sleep
from payments.emails import (
    send_welcome_email_to_traveller,
    send_booking_confirmation_email_to_traveller,
    send_payment_confirmation_email_to_traveller
)

IS_LOCAL = os.environ.get("IS_LOCAL", "False").strip().lower() == "true"

def Resend_welcome_email_to_traveller(traveller_data):
    print('\n')
    print("📩 Re Sending Welcome email for successful traveller creation.")
    send_welcome_email_to_traveller(traveller_data)
    print("✅ Welcome email Re sent from noreply to", traveller_data['email'])

def Resend_booking_confirmation_email_to_traveller(tour_booking_id, payment_id, traveller_id, dashboard_url):
    print("\n📩 Re Sending booking confirmation email for successful payment.")

    MAX_RETRY = 5

    for attempt in range(MAX_RETRY):
        try:
            sleep(1)

            tour_booking = TourBooking.objects.get(id=tour_booking_id)
            payment = Payment.objects.get(id=payment_id)
            traveller = Traveller.objects.get(id=traveller_id)

            send_booking_confirmation_email_to_traveller(
                tour_booking, payment, traveller, dashboard_url
            )

            print("✅ Booking confirmation email Re-sent successfully.\n")
            return True  # Success

        except TourBooking.DoesNotExist:
            print(f"⚠️ Attempt {attempt+1}: TourBooking {tour_booking_id} not found. Retrying in 3 seconds...")
            sleep(3)

    print("❌ Failed after all retry attempts.")
    return False

def Resend_payment_confirmation_email_to_traveller(tour_booking_id, payment_id, traveller_id, dashboard_url):
    print('\n')
    print("💰 Re Sending payment confirmation email for successful payment.")
    
    MAX_RETRY = 5

    for attempt in range(MAX_RETRY):
        try:
            # Wait a moment to ensure DB transaction is committed
            sleep(1)

            tour_booking = TourBooking.objects.get(id=tour_booking_id)
            payment = Payment.objects.get(id=payment_id)
            traveller = Traveller.objects.get(id=traveller_id)

            send_payment_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url)
            print("✅ Payment confirmation email sent successfully.\n")
            return True  # Success

        except TourBooking.DoesNotExist as e:
            print(f"⚠️ Attempt {attempt+1}: TourBooking {tour_booking_id} not found. Retrying in 3 seconds...")
            sleep(3)

    print("❌ Failed after all retry attempts.")
    return False
