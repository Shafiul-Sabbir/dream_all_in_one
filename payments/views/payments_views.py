from decimal import Decimal
import uuid
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import stripe
from authentication.models import User, Role
from payments.models import Traveller
from payments.serializers.traveller_serializers import TravellerListSerializer, TravellerSerializer
from payments.utils import checking_tour_and_creating_booking, complete_payment_by_stripe, convert_AM_PM_to_24_hour_format, convert_time_django_timefield, get_or_create_traveller_data, get_unique_username, generate_password, format_for_display
from payments.tasks import send_welcome_email_to_traveller_task
from tour.models import AvailableDate, AvailableTime, Tour
from tour.serializers.tour_booking_serializers import TourBookingSerializer
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@csrf_exempt
def createCheckout(request):
    # collecting traveller information from the request
    checkout_data = request.data
    traveller_info = checkout_data.get('traveller_info')
    tour_details = checkout_data.get('tour_details')

    required = ['company','first_name', 'last_name', 'email', 'phone', 'acceptOffers']
    if not all(field in traveller_info for field in required):
        return Response({"error": "Missing traveller data."}, status=400)
    
    # step : 1 - 2
    # 1   : Check if a traveller with the same email and phone already exists
    # 2   : If traveller does not exist, create a new user and traveller
    # 2.1 : Send welcome email to the traveller asynchronously through Celery
    traveller_response = get_or_create_traveller_data(traveller_info, [])
    if traveller_response.get("errors"):
        return Response({
            "status": "error",
            "errors": traveller_response["errors"]
        }, status=400)
    traveller_data = traveller_response["traveller_data"]
    
    # step : 3 - 5
    # 3 : get the tour from the checkout_data
    # 4 : Validate total participants and calculate total price
    # 5 : Create a booking for the tour
    booking_response = checking_tour_and_creating_booking(tour_details, traveller_data)
    if booking_response.get("errors"):
        return Response({
            "status": "error",
            "errors": booking_response["errors"]
        }, status=400)
    booking_data = booking_response["booking_data"]
    print('\n')
    print("booking_response :", booking_response)
    print('\n')
    print("booking_data :", booking_data)
    print('\n')

    # step : 6 - 7
    # creating line items for stripe payment
    # Creating Stripe Checkout session
    stripe_response = complete_payment_by_stripe(tour_details, booking_data)
    if stripe_response.get("errors"):
        return Response({
            "status": "error",
            "errors": stripe_response["errors"]
        }, status=400)
    session_url = stripe_response["session_url"]

    # ✅ Final Success Response
    return Response({
        "status": "success",
        "checkout_url": session_url,
        "traveller": traveller_data,
        "booking": booking_data
    }, status=201)


@api_view(['POST'])
def checkAvailability(request):
    """
    Check availability of a tour based on selected date and time,
    with field-wise error responses.
    """
    data = request.data.get("tour_details", {})

    tour_id = data.get('tour_id')
    selected_date = data.get('selected_date', None)
    selected_time = data.get('selected_time', None)
    total_participants = data.get('total_participants')
    total_price = Decimal(data.get('total_price')).quantize(Decimal('0.01'))
    guide = data.get('guide')

    errors = {}

    # Validate required fields
    if not tour_id:
        errors['tour_id'] = "Tour ID is required."
    if not selected_date:
        errors['selected_date'] = "Selected date is required."
    # if not selected_time:
    #     errors['selected_time'] = "Selected time is required."
    if not total_participants:
        errors['total_participants'] = "Total participants is required."

    if errors:
        return Response({"status": "error", "errors": errors}, status=400)

    # Fetch tour
    try:
        tour = Tour.objects.get(id=tour_id)
    except Tour.DoesNotExist:
        errors['tour_id'] = "Tour not found."
        return Response({"status": "error", "errors": errors}, status=404)

    # Convert time
    if selected_time is not None:
        formatted_selected_time = convert_AM_PM_to_24_hour_format(selected_time)

    # Check if the tour is guided or without guide
    guidance_tour_prices = tour.day_tour_price_list.filter(
        guide=guide,
    )
    print('\n')
    print("guidance_tour_prices: ", guidance_tour_prices)
    if selected_time is not None:
        target_tour_price = guidance_tour_prices.filter(
            available_dates__date=selected_date,
            available_times__time=formatted_selected_time
        ).first()
        print("target_tour_price: ", target_tour_price)
    else:
        target_tour_price = guidance_tour_prices.filter(
            available_dates__date=selected_date
        ).first()
        print("target_tour_price without selected_time: ", target_tour_price)
    print('\n')

    if target_tour_price is None:
        # If no guided tour found, check for any available date and time
        if selected_time is not None:
            has_matching_date_time = tour.day_tour_price_list.filter(
                available_dates__date=selected_date,
                available_times__time=formatted_selected_time
            ).exists()
            print("Has Matching Date and Time: ", has_matching_date_time)
        else:
            has_matching_date_time = tour.day_tour_price_list.filter(
                available_dates__date=selected_date
            ).exists()
            print("Has Matching Date and Time: ", has_matching_date_time)
        
        if has_matching_date_time:
            errors['guide'] = f"Selected guide '{guide}' is not available for this selected date and time."
            return Response(
                {"status": "error", "errors": errors},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # Determine which field is invalid
            print("Checking availability for date and time...")
            date_check = guidance_tour_prices.filter(available_dates__date=selected_date).exists()
            if selected_time is not None:
                time_check = guidance_tour_prices.filter(available_times__time=formatted_selected_time).exists()
            else:
                time_check = True
                
            if not date_check:
                errors['selected_date'] = f"Selected date {selected_date} is not available for guidance type '{guide}'."
            if not time_check:
                errors['selected_time'] = f"Selected time {selected_time} is not available for guidance type '{guide}'."

        return Response({"status": "error", "errors": errors}, status=status.HTTP_404_NOT_FOUND)

    # Validate total participants
    max_group_size = int(tour.group_size)
    if total_participants <= 0 or total_participants > max_group_size:
        errors['total_participants'] = f"Total participants must be between 1 and {max_group_size}."
        return Response({"status": "error", "errors": errors}, status=400)

    # Validate price
    if tour.price_by_passenger:
        expected_price = target_tour_price.price_per_person * total_participants
        if total_price != expected_price:
            print(f"total_price : {total_price}, type {type(total_price)}")
            print(f"expected_price : {expected_price}, type : {type(expected_price)}")
            errors['price_by_passenger'] = True
            errors['total_price'] = f"Incorrect total price. Expected {expected_price}."
    elif tour.price_by_vehicle:
        expected_price = target_tour_price.group_price
        if total_price != expected_price:
            errors['price_by_vehicle'] = True
            errors['total_price'] = f"Incorrect total price. Expected {expected_price}."

    if errors:
        return Response({"status": "error", "errors": errors}, status=400)

    return Response({"available": True}, status=200)

from tour.models import TourBooking
from payments.resend_emails import (
    Resend_welcome_email_to_traveller,
    Resend_booking_confirmation_email_to_traveller,
    Resend_payment_confirmation_email_to_traveller
)
@api_view(['POST'])
def resendEmail(request):
    """
    Resend welcome email to the traveller based on email and phone.
    """
    data = request.data
    booking_id = data.get('booking_id')
    with_welcome_email = data.get('with_welcome_email', False)

    if booking_id is None:
        return Response({"error": "Booking ID is required."}, status=400)
    else:
        try:
            booking_id = int(booking_id)
        except ValueError:
            return Response({"error": "Booking ID must be an integer."}, status=400)
        
    # Fetch booking instance
    booking = TourBooking.objects.filter(id=booking_id).first()
    if not booking:
        return Response({"error": "Booking not found."}, status=404)
    tour_booking_id = booking.id
    
    # finding user instance from booking
    user = booking.user
    if not user:
        return Response({"error": "User not found for the given booking."}, status=404) 
    
    # finding traveller from booking
    traveller = booking.traveller
    if not traveller:
        return Response({"error": "Traveller not found for the given booking."}, status=404)    
    traveller_id = traveller.id
    
    # finding payment from booking
    payment = booking.payment
    if not payment:
        return Response({"error": "Payment not found for the given booking."}, status=404)
    payment_id = payment.id

    company = booking.company
    print("company : ", company)

    email = user.email
    username = user.username
    print("email : ", email)
    print("username : ", username)

    dashboard_url = settings.TRAVELLER_DASHBOARD_URL


    # # generate new password as the previous one has not been received
    if with_welcome_email:
        new_password = generate_password()
        print("new_password : ", new_password)
        user.set_password(new_password)
        user.save()

        # Send welcome email asynchronously
        traveller_data = {
            "company": company.name,
            "traveller_id": traveller.id,
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": username,
            "password": new_password,
            "email": user.email,
            "phone": traveller.phone,
            "acceptOffers": traveller.accept_offers,
            "created_by": traveller.created_by,
            "updated_by": traveller.updated_by,
            "created_at": traveller.created_at,
            "updated_at": traveller.updated_at,
        }

        # Step : Send welcome email without using celery task
        traveller_data['dashboard_url'] = dashboard_url

        Resend_welcome_email_to_traveller(traveller_data)
        print("✅ Welcome email succesfully Re-sent to traveller.\n")

    Resend_booking_confirmation_email_to_traveller(
        tour_booking_id, payment_id, traveller_id, dashboard_url
    )
    print("✅ Booking confirmation email has Re-sent to traveller.\n")

    Resend_payment_confirmation_email_to_traveller(
        tour_booking_id, payment_id, traveller_id, dashboard_url
    )
    print("✅ Payment confirmation email has Re-sent to traveller.\n")

    return Response({
        "status": "success", 
        "message": "Booking & Payment confirmation email has re-sent successfully..."}, status=200
        )