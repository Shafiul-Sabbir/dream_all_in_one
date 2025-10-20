from celery import shared_task
from tour.emails import send_date_change_request_email_to_admin, send_date_change_request_approval_email_from_admin_to_traveller, send_date_change_request_deny_email_to_traveller, send_booking_cancellation_request_email_to_admin, send_booking_cancellation_request_deny_email_to_traveller, booking_cancellation_request_approval_email_from_admin_to_traveller, send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin
from payments.models import Payment, Traveller
from tour.models import TourBooking

@shared_task    
def send_date_change_request_email_to_admin_task(tour_booking_id, admin_all_booking_page_url):
    print('\n')
    print(f"Sending date change request email for notifying admin.")
    # Retriving instances from their ID
    # we will convert the filter method into get, when our full system will be automated
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    send_date_change_request_email_to_admin(tour_booking, admin_all_booking_page_url)
    print("sent date change request email from tasks.py.")
    print('\n')

@shared_task    
def send_date_change_request_approval_email_from_admin_to_traveller_task(tour_booking_id, traveller_dashboard_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    send_date_change_request_approval_email_from_admin_to_traveller(tour_booking, traveller_dashboard_url)
    print("sent date change request approval email from tasks.py.")

@shared_task
def send_date_change_request_deny_email_to_traveller_task(tour_booking_id, requested_selected_date, traveller_dashboard_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    print("sending date change request deny email to traveller from tasks.py ")
    send_date_change_request_deny_email_to_traveller(tour_booking, requested_selected_date, traveller_dashboard_url)
    print("sent date change request deny email from tasks.py.")

@shared_task
def send_booking_cancellation_request_email_to_admin_task(tour_booking_id, admin_all_booking_page_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    print(f"Sending booking cancellation request email for notifying admin.")
    send_booking_cancellation_request_email_to_admin(tour_booking, admin_all_booking_page_url)
    print("sent booking cancellation request email from tasks.py.")

@shared_task
def booking_cancellation_request_approval_email_from_admin_to_traveller_task(tour_booking_id, traveller_dashboard_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    booking_cancellation_request_approval_email_from_admin_to_traveller(tour_booking, traveller_dashboard_url)
    print("booking cancellation request approval email from tasks.py.")

@shared_task
def send_booking_cancellation_request_deny_email_to_traveller_task(tour_booking_id, traveller_dashboard_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    print("sending booking cancellation request deny email to traveller from tasks.py ")
    send_booking_cancellation_request_deny_email_to_traveller(tour_booking, traveller_dashboard_url)
    print("sent booking cancellation request deny email from tasks.py.")

@shared_task
def send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin_task(tour_booking_id, traveller_dashboard_url):
    print('\n')
    tour_booking = TourBooking.objects.get(id=tour_booking_id)
    print("sending manually cancelled booking email to traveller from tasks.py ")
    send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin(tour_booking, traveller_dashboard_url)
    print("sent manually cancelled booking email from tasks.py.")