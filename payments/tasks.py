from celery import shared_task
from payments.emails import (
    send_payment_confirmation_email_to_traveller,
    send_welcome_email_to_traveller,
    send_booking_confirmation_email_to_traveller,
)
from payments.models import Payment, Traveller
from tour.models import TourBooking
from time import sleep


# --------------------------------------------
# Welcome Email (simple)
# --------------------------------------------
@shared_task
def send_welcome_email_to_traveller_task(traveller_data):
    send_welcome_email_to_traveller(traveller_data)


# --------------------------------------------
# Booking Confirmation Email
# --------------------------------------------
@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email_to_traveller_task(self, tour_booking_id, payment_id, traveller_id, dashboard_url):
    print('\n')
    print("📩 Sending booking confirmation email for successful payment.")
    print("tour booking id from payment task before finding booking is", tour_booking_id)

    try:
        # Wait a moment to ensure DB transaction is committed
        sleep(1)

        tour_booking = TourBooking.objects.get(id=tour_booking_id)
        payment = Payment.objects.get(id=payment_id)
        traveller = Traveller.objects.get(id=traveller_id)

        send_booking_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url)
        print("✅ Booking confirmation email sent successfully.\n")

    except TourBooking.DoesNotExist as e:
        print(f"⚠️ TourBooking {tour_booking_id} not found, retrying...")
        raise self.retry(exc=e, countdown=3)  # Retry after 3 seconds

    except Exception as e:
        print("❌ Unexpected error in booking email task:", str(e))
        raise


# --------------------------------------------
# Payment Confirmation Email
# --------------------------------------------
@shared_task(bind=True, max_retries=3)
def send_payment_confirmation_email_to_traveller_task(self, tour_booking_id, payment_id, traveller_id, dashboard_url):
    print('\n')
    print("💰 Sending payment confirmation email for successful payment.")

    try:
        # Wait a moment to ensure DB transaction is committed
        sleep(1)

        tour_booking = TourBooking.objects.get(id=tour_booking_id)
        payment = Payment.objects.get(id=payment_id)
        traveller = Traveller.objects.get(id=traveller_id)

        send_payment_confirmation_email_to_traveller(tour_booking, payment, traveller, dashboard_url)
        print("✅ Payment confirmation email sent successfully.\n")

    except TourBooking.DoesNotExist as e:
        print(f"⚠️ TourBooking {tour_booking_id} not found, retrying...")
        raise self.retry(exc=e, countdown=3)  # Retry after 3 seconds

    except Exception as e:
        print("❌ Unexpected error in payment email task:", str(e))
        raise
