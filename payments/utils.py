from datetime import datetime
from decimal import Decimal
import secrets
import string
import re
import uuid
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
import stripe
from authentication.models import Role, User
from payments.models import Traveller
from payments.tasks import send_welcome_email_to_traveller_task
from tour.models import AvailableDate, AvailableTime, Tour, TourBooking
from tour.serializers.tour_booking_serializers import TourBookingSerializer
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
stripe.api_key = settings.STRIPE_SECRET_KEY

def generate_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_unique_username(first_name, last_name):
    base_username = re.sub(r'\W+', '', f"{first_name}{last_name}").lower()
    base_username = base_username[:20]

    similar_usernames = User.objects.filter(username__startswith=base_username).values_list('username', flat=True)
    
    max_suffix = 0
    for uname in similar_usernames:
        match = re.match(rf'^{re.escape(base_username)}(\d+)?$', uname)
        if match:
            suffix = match.group(1)
            if suffix and suffix.isdigit():
                max_suffix = max(max_suffix, int(suffix))

    if max_suffix == 0 and base_username not in similar_usernames:
        print(f"Username '{base_username}' is unique.")
        return base_username
    else:
        base_username = f"{base_username}{max_suffix + 1}"
        print(f"Username '{base_username}' is unique after adding suffix.")
        return base_username
    
def convert_time_django_timefield(time):
    time_str = time  # e.g. "2:30 PM"

    # Parse to datetime object first
    parsed_time = datetime.strptime(time_str, '%I:%M %p')

    # Format as 24-hour time string
    formatted_time = parsed_time.strftime('%H:%M:%S')
    
    # Use in your data
    return formatted_time

def format_for_display(data):
    """
    Recursively formats Decimal values for display purposes only.
    Original data remains unchanged.
    """
    if isinstance(data, dict):
        return {k: format_for_display(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_for_display(item) for item in data]
    elif isinstance(data, Decimal):
        return f"{data:.2f}"  # Always keep 2 decimal places
    else:
        return data
    
def convert_AM_PM_to_24_hour_format(time_str):
    """
    Convert time from AM/PM format to 24-hour format.
    """
    try:
        # Parse the time string
        parsed_time = datetime.strptime(time_str, '%I:%M %p')
        # Format it to 24-hour format
        return parsed_time.strftime('%H:%M:%S')
    except ValueError:
        raise ValueError("Time must be in 'HH:MM AM/PM' format") from None
    
def generate_booking_qr(tour_booking):
    # 1. Booking ID or URL as data
    data = f"Booking ID: {tour_booking.booking_id}"
    # optionally, you can encode a URL instead:
    # data = f"https://yourwebsite.com/booking/{tour_booking.id}/"

    # 2. Generate QR code
    qr = qrcode.QRCode(
        version=1,  # 1 = 21x21 matrix
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # 3. Save to Django FileField
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    filename = f"booking_{tour_booking.booking_id}_qr.png"

    # save to FileField in model
    tour_booking.qr_code.save(filename, ContentFile(buffer.getvalue()), save=True)
    buffer.close()

    return tour_booking.qr_code.url
    
def generate_booking_id(selected_date, booking_id):
    """
    Generate booking ID in the format: DZ-TDDMMYYID
    Example: DZ-T08072538
    """
    # Ensure selected_date is datetime.date / datetime object
    # Convert string to datetime if needed
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    print("selected_date :", selected_date)
    print("booking_id :", booking_id)
    day = selected_date.strftime("%d")   # 08
    month = selected_date.strftime("%m") # 07
    year = selected_date.strftime("%y")  # 25

    print("day : ", day)
    print("month :", month)
    print("year :", year)

    return f"DZ-T{day}{month}{year}{booking_id}"

def generate_invoice_id(selected_date, booking_id):
    """
    Generate invoice ID in the format: DZ-IDDMMYYID
    Example: DZ-I08072538
    """
    # Ensure selected_date is datetime.date / datetime object
    # Convert string to datetime if needed
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        
    day = selected_date.strftime("%d")   # 08
    month = selected_date.strftime("%m") # 07
    year = selected_date.strftime("%y")  # 25

    return f"DZ-I{day}{month}{year}{booking_id}"

    

def get_or_create_traveller_data(traveller_info, errors):

    email = traveller_info['email']
    phone = traveller_info['phone']

    # step : 1
    # Check if a traveller with the same email and phone already exists
    try:
        traveller = Traveller.objects.get(phone=phone)
        user = traveller.user
        traveller_data = {
            "traveller_id": traveller.id,
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "password": "********",
            "email": user.email,
            "phone": traveller.phone,
            "acceptOffers": traveller.accept_offers,
            "created_by": traveller.created_by,
            "updated_by": traveller.updated_by,
            "created_at": traveller.created_at,
            "updated_at": traveller.updated_at,
        }
    
    # step : 2
    # If traveller does not exist, create a new user and traveller
    except Traveller.DoesNotExist:
        try:
            username = get_unique_username(traveller_info['first_name'], traveller_info['last_name'])
            password = generate_password()
            role, _ = Role.objects.get_or_create(name="TRAVELLER")

            # creating new user
            user = User.objects.create_user(
                first_name=traveller_info['first_name'],
                last_name=traveller_info['last_name'],
                email=email,
                gender="",
                password=password,
                primary_phone=phone,
            )
            user.username = username
            user.role = role
            user.save()

            # creating new traveller
            traveller = Traveller.objects.create(
                user=user,
                phone=phone,
                accept_offers=traveller_info['acceptOffers'],
                created_by=username,
                updated_by=username
            )

            traveller_data = {
                "traveller_id": traveller.id,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": username,
                "password": password,
                "email": email,
                "phone": traveller.phone,
                "acceptOffers": traveller.accept_offers,
                "created_by": traveller.created_by,
                "updated_by": traveller.updated_by,
                "created_at": traveller.created_at,
                "updated_at": traveller.updated_at
            }


            # step : 2.1
            # Send welcome email to the traveller asynchronously through Celery
            dashboard_url = settings.TRAVELLER_DASHBOARD_URL
            traveller_data['dashboard_url'] = dashboard_url
            # print("traveller_data", traveller_data)
            send_welcome_email_to_traveller_task.delay(traveller_data)
            print("welcome email sent to traveller.")
            print('/n')
        except Exception as e:
            errors.append(f"Traveller creation failed: {str(e)}")
            return {
            "errors": errors,
            "traveller_data": None
            }

    return {
        "errors" : errors,
        "traveller_data" : traveller_data if not errors else None,
    }

def checking_tour_and_creating_booking(tour_details, traveller_data):
    errors = []
    booking_response = {}

    tour_id = tour_details.get('tour_id')
    selected_date = tour_details.get('selected_date', None)
    selected_time = tour_details.get('selected_time', None)
    guide = tour_details.get('guide')

    print("selected date is :", selected_date)
    print("selected time is :", selected_time)

    try:
        # 1) ট্যুর বের করা
        tour = Tour.objects.get(id=tour_id)

        # 2) ট্যুরের প্রাইস লিস্ট (যার মধ্যে available_dates/available_times আছে)
        tour_price_list = tour.day_tour_price_list.filter(
        guide=guide,
    )
        print("Tour Price List:", tour_price_list)

        price_per_person = None
        group_price = None

        # granular flags
        found_match = False              # date & time দুটোই মিলে গেছে কিনা
        any_date_match = False           # অন্তত একটি price-row এ date মিলে গেছে কিনা
        any_time_for_that_date = False   # date মেলার সাথে সেই row-এ time-ও মিলে গেছে কিনা

        # ইনপুট time টাকে 24-hour format এ কনভার্ট করি (DB TimeField match করার জন্য)
        if selected_time is not None:
            formatted_selected_time = convert_AM_PM_to_24_hour_format(selected_time)

        for tour_price in tour_price_list:
            print("Tour Price:", tour_price)

            # date check
            available_dates_qs = tour_price.available_dates.filter(date=selected_date)
            date_exists = available_dates_qs.exists()
            print("Available Dates:", available_dates_qs)

            if date_exists:
                any_date_match = True  # অন্তত এক জায়গায় date match হয়েছে

                # time check (শুধু date match হলে তবেই time check করবো)
                if selected_time is not None:
                    available_times_qs = tour_price.available_times.filter(time=formatted_selected_time)
                    time_exists = available_times_qs.exists()
                    print("Available Times:", available_times_qs)

                    if time_exists:
                        any_time_for_that_date = True
                        # দুটোই মিললে success branch
                        price_per_person = tour_price.price_per_person
                        group_price = tour_price.group_price
                        found_match = True
                        print(f"Tour {tour.name} is available on {selected_date} at {selected_time}.")
                        print(f"Price per person: {price_per_person}, Group price: {group_price}, Guide: {guide}")
                        print('\n')
                        break  # একবার পেলেই break
                else: #if traveller does not select any time for that day.
                    found_match = True
                    any_time_for_that_date = True
                    price_per_person = tour_price.price_per_person
                    group_price = tour_price.group_price

        # লুপ শেষে granular error গুলো সেট করো
        if not found_match:
            if not any_date_match:
                errors.append(f"No available dates for the selected tour on {selected_date}.")
            elif not any_time_for_that_date:
                errors.append(f"No available time {selected_time} on {selected_date} for this tour.")
            return {"errors": errors}

    except Tour.DoesNotExist:
        errors.append("Tour not found.")
        return {"errors": errors}
    except Exception as e:
        errors.append(str(e))
        return {"errors": errors}

    if found_match:
        print("tour, price_per_person, group_price and guide found successfully.")

    # 4) অংশগ্রহণকারী সংখ্যা validate + মোট দাম
    total_participants = tour_details.get('total_participants')
    if not total_participants:
        errors.append("Total participants must be provided for this tour.")
        return {"errors": errors}
    elif total_participants <= 0 or total_participants > int(tour.group_size):
        errors.append(f"Total participants must be between 0 to {tour.group_size}")
        return {"errors": errors}

    given_total_price = tour_details.get('total_price')
    if tour.price_by_passenger:
        total_price = total_participants * price_per_person
    elif tour.price_by_vehicle:
        total_price = group_price
    else:
        errors.append("Tour pricing method is not defined.")
        return {"errors": errors}
    
    if given_total_price != total_price:
        errors.append(f"You have to pay {total_price} USD only.")
        return {"errors": errors}

    print(f"Total participants: {total_participants}, Total price: {total_price}")

    # step : 5

    # Create a booking for the tour
    try:
        if selected_time is not None:
            selected_time = convert_time_django_timefield(selected_time)
        else:
            selected_time = None

        tour_booking_data = {
            "tour":tour.id,        
            "guide": guide,
            "traveller": traveller_data['traveller_id'],
            "user": traveller_data['user_id'],
            "total_participants": total_participants,
            "selected_date": selected_date,
            "selected_time": selected_time,
            "price_by_passenger": tour.price_by_passenger,
            "price_per_person": price_per_person if tour.price_by_passenger else Decimal(0.00),
            "price_by_vehicle": tour.price_by_vehicle,
            "group_price": group_price if tour.price_by_vehicle else Decimal(0.00),
            "total_price": total_price,
            "created_by": traveller_data['username'],
            "updated_by": traveller_data['username'],
        }
        print("Booking Data : ", format_for_display(tour_booking_data))
        # print("type of total_price in booking_data : ", type(tour_booking_data['total_price']))
        print('/n')
        tour_booking_serializer = TourBookingSerializer(data=tour_booking_data)
        if tour_booking_serializer.is_valid():
            tour_booking = tour_booking_serializer.save()
            print("Booking Created successfully:", tour_booking)
            print("tour booking id is : ", tour_booking.id)

            # generating booking_id from custom function and saving it to the tour_booking instance. 
            booking_id = generate_booking_id(selected_date, tour_booking.id)
            print("booking id is : ", booking_id)
            tour_booking.booking_id = booking_id
            tour_booking.save()

            # generating qr from booking_id 
            qr_url = generate_booking_qr(tour_booking)
            qr_url = f"{settings.API_SITE_URL}{qr_url}"
            print("qr url is :", qr_url)
            tour_booking.qr_url = qr_url
            tour_booking.save()

            # generating uuid for booking_uuid
            booking_uuid = uuid.uuid4()
            tour_booking.booking_uuid = booking_uuid
            tour_booking.save()

            booking_response = tour_booking_data
            booking_response['tour_name'] = tour.name
            booking_response['tour_booking_id'] = tour_booking.id
            booking_response['traveller_email'] = traveller_data['email']
            booking_response['booking_uuid'] = booking_uuid
            print('/n')

        else:
            # return Response(tour_booking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            errors.append(tour_booking_serializer.errors)

    except Exception as e:
        errors.append(str(e))
    
    return {
        "errors": errors,
        "booking_data": booking_response if not errors else None
    }

def complete_payment_by_stripe(tour_details, booking_response ):
    # step : 6
    # creating line items for stripe payment
    print('\n')
    print("starting payment process using stripe.")
    print('\n')
    print("booking response from stripe : ", booking_response)
    print('\n')


    errors = []
    session_url = None
    tour_id = tour_details.get('tour_id')
    tour = Tour.objects.filter(id=tour_id).first()
    if not tour:
        errors.append("Tour not found for payment.")
        return {
            "errors": errors,
            "session_url": None
        }
    print("tour found for payment : ", tour.name)
    session = None

    # getting tour image url
    tour_image_url = [tour.cloudflare_thumbnail_image_url] if tour.cloudflare_thumbnail_image_url else []
    print("tour image url : ", tour_image_url)
    try:
        line_items = []
        line_items.append({
            'price_data': {
                'currency': 'USD',
                'product_data': {
                    'name': f"{booking_response['tour_name']} Booking",
                    'description': f"Booking for {tour_details['total_participants']} participants on {tour_details['selected_date']} at {tour_details['selected_time'] if tour_details['selected_time'] is not None else None}",
                    "images": tour_image_url,
                },
                'unit_amount': int(booking_response['total_price'] * 100),  # Stripe expects amount in cents
            },
            'quantity': 1,  # Only one booking per session
        })
        print("is local : ", settings.IS_LOCAL)
        booking_uuid = str(booking_response['booking_uuid'])
        print("booking_uuid : ", booking_uuid)
        if settings.IS_LOCAL:
            success_url = f"http://192.168.68.111:3000/success?booking_id={booking_uuid}"
        else:
            success_url = f"https://dreamziarah.com/success?booking_id={booking_uuid}"

        
        if tour_details['cancel_url'] is None:
            cancel_url = None
        else:
            cancel_url = tour_details['cancel_url']
        print("success url : ", success_url)
        print("cancel url : ", cancel_url)

        print('\n')


        # step : 7
        # Create Stripe Checkout session
        try:
            print("Creating Stripe Checkout session...")
            # Get Dhaka time (localtime according to settings.py)
            now_in_dhaka = timezone.localtime(timezone.now())

            print("now (Dhaka):", now_in_dhaka)

            # Add 24 hours to Dhaka time
            expires_at = int((now_in_dhaka + timedelta(hours=24)).timestamp())

            print(f"Session will expire at: {expires_at} (UNIX timestamp)")

            session = stripe.checkout.Session.create(
                payment_method_types=['card','klarna'],  # Only card payment method
                line_items=line_items,
                mode="payment",
                success_url = success_url,
                cancel_url = cancel_url,
                customer_email=booking_response['traveller_email'],
                billing_address_collection="required",

                metadata={
                    # 'session_id' : session['id'],
                    'tour_booking_id': booking_response['tour_booking_id'],
                    "currency": "USD",
                    "success_url" : success_url,
                },
                # expires_at=expires_at,  # 30min–24h
                # after_expiration={"recovery": {"enabled": True}},  # recovery URL
            )
            print(f"stripe session created successfully, session id is : {session['id']}")

            tour_booking = TourBooking.objects.get(id = booking_response['tour_booking_id'])
            tour_booking.payment_url = session.url
            tour_booking.save()
            print("tour booking payment url saved successfully.")
            #   session URL
            print("Returning checkout URL .:",  session.url) 
        except Exception as e:
            print("Session creation error: ", str(e))
            errors.append(str(e))
            # return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        errors.append(f"Stripe Payment Error: {str(e)}")

    return {
        "errors": errors,
        "session_url": session.url if session is not None else "seesion not created"
    }
