from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from decimal import Decimal
from payments.models import Traveller
from tour.serializers.tour_booking_serializers import TourBookingListSerializer, TourBookingSerializer
from tour.models import CancellationPolicy, TourBooking
from tour.tasks import send_date_change_request_email_to_admin_task, send_date_change_request_approval_email_from_admin_to_traveller_task, send_date_change_request_deny_email_to_traveller_task, send_booking_cancellation_request_email_to_admin_task, send_booking_cancellation_request_deny_email_to_traveller_task, send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin_task
from tour.tasks import booking_cancellation_request_approval_email_from_admin_to_traveller_task
from rest_framework import status
from commons.pagination import Pagination
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, time
from django.utils import timezone
from payments.utils import generate_booking_qr
import stripe
import uuid
from urllib.parse import urlparse
stripe.api_key = settings.STRIPE_SECRET_KEY

# from silk.profiling.profiler import silk_profile

@api_view(['POST'])
def createTourBooking(request):
    """
    Create a new tour booking.
    """
    data = request.data
    serializer = TourBookingSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
# @silk_profile()
def getAllTourBooking(request):
    company_id = request.query_params.get('company_id')
    if company_id:
        tour_bookings = TourBooking.objects.filter(company__id=company_id).select_related('tour', 'traveller', 'user', 'payment')

    total_elements = tour_bookings.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    tour_bookings = pagination.paginate_data(tour_bookings)

    serializer = TourBookingListSerializer(tour_bookings, many=True)

    response = {
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
        'tour_bookings': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def getAllTourBookingByTravellerID(request, pk):
    # print("pk is : ", pk)
    try:
        traveller = Traveller.objects.get(pk=pk)
    except Traveller.DoesNotExist:
        return Response({'error': 'Traveller not found'}, status=404)
    
    # print("traveller : ", traveller)

    # ✅ Corrected line here
    tour_bookings = TourBooking.objects.filter(traveller=traveller).select_related('tour', 'user')
    # tour_bookings = TourBooking.objects.filter(traveller=traveller)
    # print("tour bookings :", tour_bookings)

    total_elements = tour_bookings.count()
    paid = tour_bookings.filter(status='paid').count()
    pending = tour_bookings.filter(status='pending').count()
    cancelled = tour_bookings.filter(cancellation_status='approved').count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    tour_bookings = pagination.paginate_data(tour_bookings)

    serializer = TourBookingListSerializer(tour_bookings, many=True)

    response = {
        'tour_bookings': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
        'paid': paid,
        'pending': pending,
        'cancelled': cancelled,
    }

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllTourBookingWithoutPagination(request):
    company_id = request.query_params.get('company_id')
    if company_id:
        tour_bookings = TourBooking.objects.filter(company__id=company_id).select_related('tour', 'traveller', 'user', 'payment')

    total_elements = tour_bookings.count()
    serializer = TourBookingListSerializer(tour_bookings, many=True)
    response = {
        'total_elements': total_elements,
        'tour_bookings': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def getATourBooking(request, pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        serializer = TourBookingListSerializer(tour_booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour Booking with id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getATourBookingByBookingUUID(request, booking_uuid):
    try:
        tour_booking = TourBooking.objects.get(booking_uuid=booking_uuid)
        serializer = TourBookingListSerializer(tour_booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour Booking with booking_uuid - {booking_uuid} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
def updateTourBooking(request,pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        data = request.data
        print("data :", data)
        
        serializer = TourBookingSerializer(tour_booking, data=data)
        if serializer.is_valid():
            serializer.save()
         
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def requestToUpdateATourBookingDate(request):
    data = request.data
    print(data)
    booking_id = data.get("booking_id")
    selected_date = data.get("selected_date")
    try:
        tour_booking = TourBooking.objects.get(id=booking_id)
        tour_booking.date_change_request = True
        tour_booking.requested_selected_date = selected_date
        tour_booking.date_request_approved = False
        tour_booking.date_change_request_status = 'reviewing'
        tour_booking.save()
        response_data = {
            "booking_id": booking_id,
            "date_change_request" : True,
            "selected_date" : selected_date,
        }

        # sending mail from sales to admin for informing the request 

        admin_all_booking_page_url = settings.ADMIN_ALL_BOOKING_PAGE

        print("admin all booking page : ", admin_all_booking_page_url)
        print("sending mail to admin for notifying date change request.")
        send_date_change_request_email_to_admin_task(booking_id, admin_all_booking_page_url)
        print("successfully sent mail to the admin.")

        return Response(response_data, status=status.HTTP_201_CREATED)
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {booking_id} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def approveDateChangeRequest(request, pk):
    data = request.data
    selected_date = data.get("selected_date")
    date_change_request = data.get("date_change_request")
    try:
        tour_booking = TourBooking.objects.get(id=pk)
        booking_id = tour_booking.id
        if tour_booking.date_change_request and tour_booking.date_change_request_status == 'reviewing':
            tour_booking.previous_selected_date = tour_booking.selected_date
            tour_booking.selected_date = selected_date
            tour_booking.date_change_request = date_change_request
            tour_booking.requested_selected_date = None
            tour_booking.date_request_approved = True
            tour_booking.date_change_request_status = 'approved'
            # If the date is changed, cancellation eligibility will be false for this booking forever.
            tour_booking.cancellation_eligible = False

            tour_booking.save()

            response_data = {
                "booking_id": pk,
                "date_change_request" : False,
                "Present_selected_date" : tour_booking.selected_date,
                "Previous_selected_date" : tour_booking.previous_selected_date,
                "date_request_approved": True,
                "date_change_request_status": "approved"
            }
            traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
            print("sending date change request approval email from admin to traveller")
            send_date_change_request_approval_email_from_admin_to_traveller_task(booking_id, traveller_dashboard_url)
            print("date change request approval email sent successfully.")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No pending date change request to approve.'}, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {pk} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def denyDateChangeRequest(request, pk):
    try:
        tour_booking = TourBooking.objects.get(id=pk)
        booking_id = tour_booking.id
        if tour_booking.date_change_request and tour_booking.date_change_request_status == 'reviewing':
            # Simply reset the request fields without changing the selected_date
            requested_selected_date = tour_booking.requested_selected_date
            tour_booking.date_change_request = False
            tour_booking.requested_selected_date = None
            tour_booking.date_request_approved = False
            tour_booking.date_change_request_status = 'denied'
            tour_booking.save()
            response_data = {
                "booking_id": pk,
                "date_change_request" : False,
                "selected_date" : tour_booking.selected_date,
                "date_request_approved": False,
                "date_change_request_status": "denied"
            }

            traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
            print("sending date change request deny email from admin to traveller")
            send_date_change_request_deny_email_to_traveller_task(booking_id, requested_selected_date,traveller_dashboard_url)
            print("date change request deny email sent successfully.")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No pending date change request to deny.'}, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {pk} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)


def format_duration(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(days)}d {int(hours)}h {int(minutes)}m"

def calculate_refund(tour_booking, custom_diff_total_seconds, policy_list):
    """
    Refund calculation logic আলাদা ফাংশনে
    """
    largest_threshold = policy_list[0][0] if policy_list else None
    print("largest_threshold:", largest_threshold)
    minimum_threshold = policy_list[-1][0] if policy_list else None
    print("minimum_threshold:", minimum_threshold)
    applicable_policy = None
    refund_percentage = Decimal('0.00')

    # handle case when custom_diff_total_seconds is smaller than minimum threshold
    if minimum_threshold is not None and custom_diff_total_seconds < minimum_threshold:
        print("custom_diff_total_seconds is smaller than minimum threshold")
        refund_percentage = Decimal('0.00')
        applicable_policy = None  # কোনো নির্দিষ্ট policy না
        # refunded_amount = (refund_percentage / Decimal('100.00')) * tour_booking.total_price
        print(f"from lower than minimum threshold refund_percentage: {refund_percentage}, applicable_policy: {applicable_policy}")
        # return refund_percentage, refunded_amount, None  # এখানে কোনো specific policy নেই

    # Check ladder (ধরে নিচ্ছি policy_list ordered descending)
    for threshold, policy in policy_list:
        if custom_diff_total_seconds >= threshold:
            applicable_policy = policy
            refund_percentage = policy.refund_percentage
            print("Applicable policy found :", applicable_policy)
            print(f"Threshold: {threshold}, Refund Percentage: {refund_percentage}%")
            break
    print(f"After loop - refund_percentage: {refund_percentage}, applicable_policy: {applicable_policy}" )
    print('\n')

    # যদি সবথেকে বড় threshold এর চেয়ে বেশি gap থাকে → Full refund
    # if largest_threshold is not None and custom_diff_total_seconds > largest_threshold:
    #     refund_percentage = Decimal('100.00')
    #     applicable_policy = None  # কোনো নির্দিষ্ট policy না

    print(f"Final - refund_percentage: {refund_percentage}, applicable_policy: {applicable_policy}" )

    refunded_amount = (refund_percentage / Decimal('100.00')) * tour_booking.total_price
    print(f"refunded_amount: {refunded_amount}")

    if applicable_policy:
        applicable_policy_id = applicable_policy.id
    else:
        applicable_policy_id = None

    return refund_percentage, refunded_amount, applicable_policy_id



@api_view(['GET'])
def requestToCheckCancellationPolicies(request, pk):
    try:
        tour_booking = TourBooking.objects.get(id=pk)
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {pk} doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

    tour = tour_booking.tour
    all_cancellation_policies = tour.cancellation_policies_list.all()
    applied_policy = all_cancellation_policies.filter(default_policy=True).first()

    if not applied_policy:
        return Response({'error': "No default cancellation policy found for this tour."}, status=status.HTTP_400_BAD_REQUEST)

    applied_policy_id = applied_policy.id
    policy_type = applied_policy.policy_type

    # current time
    now_utc = timezone.now()
    localtime = timezone.localtime(now_utc)

    # original event datetime
    if tour_booking.selected_time is not None:
        original_event_datetime = datetime.combine(tour_booking.selected_date, tour_booking.selected_time)
    else:
        original_event_datetime = datetime.combine(tour_booking.selected_date, time.min)

    original_event_datetime = timezone.make_aware(original_event_datetime, timezone.get_current_timezone())
    original_diff = original_event_datetime - localtime
    original_total_seconds = int(original_diff.total_seconds())
    print("original total seconds :", original_total_seconds)

    # breakdown original time difference
    original_remaining_days = original_total_seconds // 86400
    original_remaining_hours = (original_total_seconds % 86400) // 3600
    original_remaining_minutes = (original_total_seconds % 3600) // 60
    original_remaining_seconds = original_total_seconds % 60

    # custom event datetime (00:00:00 of the event day)
    custom_event_datetime = datetime.combine(tour_booking.selected_date, time.min)
    custom_event_datetime = timezone.make_aware(custom_event_datetime, timezone.get_current_timezone())
    print("custom_event_datetime:", custom_event_datetime)
    custom_diff = custom_event_datetime - localtime
    custom_total_seconds = int(custom_diff.total_seconds())
    print("custom_total_seconds:", custom_total_seconds)

    # breakdown custom time difference
    custom_remaining_days = custom_total_seconds // 86400
    custom_remaining_hours = (custom_total_seconds % 86400) // 3600
    custom_remaining_minutes = (custom_total_seconds % 3600) // 60
    custom_remaining_seconds = custom_total_seconds % 60

    # initialize default values
    refund_percentage = Decimal('0.00')
    refunded_amount = Decimal('0.00')
    refund_eligible = False
    simple_cutoff_hours = None
    applied_penalty_rule_id = None
    cutoff_hours = None
    all_penalty_rules = []
    published_policy_list = []
    cancellation_policy = {}

    # cancellation policy calculation
    if policy_type == "simple":
        simple_cutoff_hours = applied_policy.simple_cutoff_hours
        simple_cutoff_seconds = simple_cutoff_hours * 60 * 60
        if custom_total_seconds > simple_cutoff_seconds:
            refund_percentage = Decimal('100.00')
            refunded_amount = tour_booking.total_price
            refund_eligible = True
            rule_range = f"Cancellation fee of 100% is charged if cancelled {simple_cutoff_hours} hours or less before the event, otherwise 0% will be charged."
            cancellation_policy["type"] = policy_type
            cancellation_policy["range"] = rule_range
            cancellation_policy["refund_percentage"] = Decimal('100.00')
            published_policy_list.append(
                cancellation_policy
            )
        if custom_total_seconds <= simple_cutoff_seconds:
            rule_range = f"Cancellation fee of 100% is charged if cancelled {simple_cutoff_hours} hours or less before the event, otherwise 0% will be charged."
            cancellation_policy["type"] = policy_type
            cancellation_policy["range"] = rule_range
            cancellation_policy["refund_percentage"] = Decimal('0.00')
            published_policy_list.append(
                cancellation_policy
            )


    elif policy_type == "full_refund":
        if custom_total_seconds > 0:
            refund_percentage = Decimal('100.00')
            refunded_amount = tour_booking.total_price
            refund_eligible = True
            rule_range = f"Cancellation fee of 0.00% is charged if cancelled any time before starting the event."
            cancellation_policy["type"] = policy_type
            cancellation_policy["range"] = rule_range
            cancellation_policy["refund_percentage"] = refund_percentage
            published_policy_list.append(
                cancellation_policy
            )


    elif policy_type == "non_refundable":
        rule_range = f"Cancellation fee of 100.00% is charged if cancelled the booking."
        cancellation_policy["type"] = policy_type
        cancellation_policy["range"] = rule_range
        cancellation_policy["refund_percentage"] = Decimal("0.00")
        published_policy_list.append(
            cancellation_policy
        )

    elif policy_type == "advanced":
        all_penalty_rules = applied_policy.penalty_rules.all().order_by('cutoff_hours')
        print('\n')
        for rule in all_penalty_rules:
            print(f"rule id {rule.id} cutoff hours : {rule.cutoff_hours}" )
        print('\n')

        if custom_total_seconds < 0:
            refund_percentage = Decimal('0.00')
            refunded_amount = Decimal('0.00')
            refund_eligible = False
            
        elif all_penalty_rules.exists():
            largest_threshold_seconds = all_penalty_rules.last().cutoff_hours * 60 * 60
            if custom_total_seconds > largest_threshold_seconds:
                refund_percentage = Decimal('100.00')
                refunded_amount = tour_booking.total_price
                refund_eligible = True
            else:
                for rule in all_penalty_rules:
                    applied_penalty_rule_id = rule.id
                    cutoff_hours = rule.cutoff_hours
                    cutoff_seconds = cutoff_hours * 60 * 60

                    if custom_total_seconds <= cutoff_seconds:
                        print("applied rule id : ", rule.id)
                        print("custom total seconds : ", custom_total_seconds)
                        print("cutoff_seconds : ", cutoff_seconds)
                        cancellation_percentage = rule.percentage
                        print("cancellation percentage : ", cancellation_percentage)
                        refund_percentage = Decimal('100.00') - cancellation_percentage
                        print("refund percentage : ", refund_percentage)
                        refunded_amount = (tour_booking.total_price * refund_percentage) / Decimal('100.00')
                        refund_eligible = True
                        break
    else:
        return Response({"error": "Invalid policy_type"}, status=status.HTTP_400_BAD_REQUEST)

    # prepare published policy list
    if all_penalty_rules:
        for rule in all_penalty_rules:
            cancellation_policy = {}
            print("rule id :", rule.id)
            print("rule percentage : ", rule.percentage)
            rule_range = f"Cancellation fee of {rule.percentage}% is charged if cancelled {rule.days_before} days and {rule.hours_before} hours or less before the event"
            cancellation_policy["type"] = "advanced"
            cancellation_policy["range"] = rule_range
            cancellation_policy["refund_percentage"] = Decimal('100.00') - rule.percentage
            published_policy_list.append(
                cancellation_policy
            )

    # prepare response
    response_data = {
        "booking_id": tour_booking.id,
        "tour_id": tour_booking.tour.id,
        "policy_type": policy_type,
        "refund_eligible": refund_eligible,
        "has_any_tour_cancellation_policy": True if policy_type == "advanced" and all_penalty_rules else False,
        "applied_cancellation_policy_id": applied_policy_id,
        "simple_cutoff_hours": simple_cutoff_hours if policy_type == "simple" else None,
        "applied_penalty_rule_id": applied_penalty_rule_id if policy_type == "advanced" else None,
        "cutoff_hours": cutoff_hours if policy_type == "advanced" else None,
        "refund_percentage": refund_percentage,
        "refunded_amount": refunded_amount,
        "all_times": {
            "tour_date": tour_booking.selected_date,
            "tour_time": tour_booking.selected_time if tour_booking.selected_time is not None else None,
            "current_date": localtime.date(),
            "current_time": localtime.strftime("%H:%M:%S"),
        },
        "original_remaining_times": {
            "original_remaining_days": original_remaining_days,
            "original_remaining_hours": original_remaining_hours,
            "original_remaining_minutes": original_remaining_minutes,
            "original_remaining_seconds": original_remaining_seconds,
        },
        "custom_remaining_times": {
            "custom_remaining_days": custom_remaining_days,
            "custom_remaining_hours": custom_remaining_hours,
            "custom_remaining_minutes": custom_remaining_minutes,
            "custom_remaining_seconds": custom_remaining_seconds
        },
        "published_policy_list": published_policy_list
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])    
def requestToCancelTourBooking(request, pk):

    data = request.data
    print("data :", data)
    cancellation_request = data.get('cancellation_request')
    cancellation_reason = data.get('cancellation_reason')
    
    if not cancellation_request or cancellation_request is None:
        return Response({"error ": "cancellation request is required."}, status=status.HTTP_404_NOT_FOUND)
    
    if not cancellation_reason or cancellation_reason is None:
        return Response({"error ": "cancellation reason is required."}, status=status.HTTP_404_NOT_FOUND)
    

    # ths api will work when user will request for cancellation to the admin after hitting the 
    try:
        tour_booking = TourBooking.objects.get(id=pk)
        booking_id = tour_booking.id
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {tour_booking.id} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)
    
    if tour_booking.cancellation_denied_count >= 3:
        return Response({'error': 'Cancellation request has been denied 3 times. Further requests are not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    
    tour = tour_booking.tour
    all_cancellation_policies = tour.cancellation_policies_list.all()
    applied_policy = all_cancellation_policies.filter(default_policy=True).first()

    if not applied_policy:
        return Response({'error': "No default cancellation policy found for this tour."}, status=status.HTTP_400_BAD_REQUEST)

    applied_policy_id = applied_policy.id
    policy_type = applied_policy.policy_type

    # Refund হিসাব (Helper ফাংশন থেকে)
    # finding custom event datetime (tour_date + 00:00:00)
    now_utc = timezone.now()  # UTC
    localtime = timezone.localtime(now_utc)  # Convert to Asia/Dhaka

    custom_event_datetime = datetime.combine(tour_booking.selected_date, time.min)
    custom_event_datetime = timezone.make_aware(custom_event_datetime, timezone.get_current_timezone())

    # custom difference বের করা
    custom_diff = custom_event_datetime - localtime
    custom_total_seconds = int(custom_diff.total_seconds())


    # initialize default values
    refund_percentage = Decimal('0.00')
    refunded_amount = Decimal('0.00')
    refund_eligible = False
    simple_cutoff_hours = None
    applied_penalty_rule_id = None
    cutoff_hours = None
    all_penalty_rules = []


    # cancellation policy calculation
    if policy_type == "simple":
        simple_cutoff_hours = applied_policy.simple_cutoff_hours
        simple_cutoff_seconds = simple_cutoff_hours * 60 * 60
        if custom_total_seconds > simple_cutoff_seconds:
            refund_percentage = Decimal('100.00')
            refunded_amount = tour_booking.total_price
            refund_eligible = True

    elif policy_type == "full_refund":
        if custom_total_seconds > 0:
            refund_percentage = Decimal('100.00')
            refunded_amount = tour_booking.total_price
            refund_eligible = True

    elif policy_type == "non_refundable":
        pass  # already defaults to 0 refund

    elif policy_type == "advanced":
        all_penalty_rules = applied_policy.penalty_rules.all().order_by('cutoff_hours')

        if custom_total_seconds < 0:
            refund_percentage = Decimal('0.00')
            refunded_amount = Decimal('0.00')
            refund_eligible = False
        elif all_penalty_rules.exists():
            largest_threshold_seconds = all_penalty_rules.last().cutoff_hours * 60 * 60
            if custom_total_seconds > largest_threshold_seconds:
                refund_percentage = Decimal('100.00')
                refunded_amount = tour_booking.total_price
                refund_eligible = True
            else:
                for rule in all_penalty_rules:
                    applied_penalty_rule_id = rule.id
                    cutoff_hours = rule.cutoff_hours
                    cutoff_seconds = cutoff_hours * 60 * 60

                    if custom_total_seconds <= cutoff_seconds:
                        cancellation_percentage = rule.percentage
                        refund_percentage = Decimal('100.00') - cancellation_percentage
                        refunded_amount = (tour_booking.total_price * refund_percentage) / Decimal('100.00')
                        refund_eligible = True
                        break
    else:
        return Response({"error": "Invalid policy_type"}, status=status.HTTP_400_BAD_REQUEST)

    if cancellation_request == True:
        print("inside cancellation request.")
        tour_booking.cancellation_request = True
        tour_booking.cancellation_status = 'reviewing'
        tour_booking.cancellation_reason = cancellation_reason
        tour_booking.refund_percentage = refund_percentage
        tour_booking.requested_refund_amount = refunded_amount 
        tour_booking.refund_status = 'pending'
        tour_booking.save()

    serializer = TourBookingListSerializer(tour_booking)
    if serializer.is_valid:
        tour_booking = serializer.data
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # sending mail from sales to admin for informing the request 
    admin_all_booking_page_url = settings.ADMIN_ALL_BOOKING_PAGE
    print("admin all booking page : ", admin_all_booking_page_url)
    print("sending mail to admin for notifying booking cancellation request.")
    send_booking_cancellation_request_email_to_admin_task(booking_id, admin_all_booking_page_url)
    print("successfully sent mail to the admin.")

    return Response({"status": "OK",
                     "refund_eligible": refund_eligible,
                     "applied_cancellation_policy_id": applied_policy_id,
                     "refund_percentage": refund_percentage,
                     "refunded_amount": refunded_amount,
                     "tour_booking": tour_booking}, status=status.HTTP_200_OK)


@api_view(["POST"])
def approveBookingCancellationRequest(request, pk):
    """
    refundBalanceFromStripeToTraveller.....
    Refund a paid booking back to the original card.
    Request (JSON):
      {
        "amount":  null or integer minor units (e.g., 5000 for 50.00), optional -> defaults to full remaining,
        "reason":  "requested_by_customer" | "duplicate" | "fraudulent" (optional)
      }
    """
    PAID_STATUSES = {"paid"}  # adjust to your project

    try:
        booking = TourBooking.objects.get(id=pk)
        booking_id = booking.id
    except ObjectDoesNotExist:
        return Response({"detail": f"Booking {pk} not found."}, status=status.HTTP_404_NOT_FOUND)

    # 1) if booking is not in a PAID state, we just approve the cancellation without refund.
    if str(getattr(booking, "status", "")).lower() not in PAID_STATUSES:
        booking.status = "cancelled"
        booking.refund_status = "unpaid" # as user has not paid any amount and now he requests to cancel the booking 
        booking.cancellation_status = "approved"
        booking.cancellation_request = False
        booking.save(update_fields=["status", "refund_status", "cancellation_status", "cancellation_request"])

        # 🧩 NEW PART — Invalidate Stripe Session
        try:
            if booking.payment_url:
                # payment_url থেকে session_id বের করা
                # session_id থাকে এরকম: https://checkout.stripe.com/c/pay/cs_test_a1B2C3...
                url = booking.payment_url
                print('\n')
                print("payment url is :", url)
                # fragment বাদ দিয়ে শুধু path বের করা
                path = urlparse(url).path
                print('\n')
                print("path is :", path)
                # এখন শেষের অংশটা নাও
                session_id = path.split("/")[-1]
                print('\n')
                print(session_id)
                stripe.checkout.Session.expire(session_id)
                print(f"✅ Stripe session expired for booking ID {booking.id}")
        except Exception as e:
            print(f"⚠️ Failed to expire Stripe session: {e}")

        return Response({
            "detail": "Booking is not in a refundable (paid) state but cancellation request has been approved and Stripe session has been expired.",
            "booking_id": booking_id,
        }, status=status.HTTP_202_ACCEPTED)
    
    # 2) Get body inputs if we have to customize the refund ammount.
    # if we want to refund the whole amount
    amount = booking.requested_refund_amount
    reason = "requested_by_customer"

    if amount == 0:
        booking.status = "cancelled without refund"
        booking.refund_status = "cancelled without refund"  
        booking.cancellation_status = "approved"
        booking.cancellation_request = False
        booking.cancellation_eligible = False
        booking.save(update_fields=["status", "refund_status", "cancellation_status", "cancellation_request", "cancellation_eligible"])

        traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
        print("sending booking cancellation request approval email from admin to traveller")
        booking_cancellation_request_approval_email_from_admin_to_traveller_task(booking_id, traveller_dashboard_url)
        print("booking cancellation request approval email sent successfully.")

        return Response({
            "detail": "cancelled without refund.",
            "booking_id": booking_id,
        }, status=status.HTTP_202_ACCEPTED)

    # 3) Retrieve the PaymentIntent from Stripe
    payment_intent_id = getattr(booking, "payment_key", None)
    print("payment_intent_id :", payment_intent_id)
    if not payment_intent_id:
        return Response({"detail": "No Stripe payment key (Payment Intent ID) stored on booking."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pi = stripe.PaymentIntent.retrieve(payment_intent_id)
    except stripe.error.StripeError as e:
        return Response({"detail": "Failed to retrieve Payment Intent from Stripe.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    # Determine remaining refundable amount (in minor units)
    amount_received = int(pi.get("amount_received") or 0)
    amount_refunded = int(pi.get("amount_refunded") or 0)
    remaining = max(amount_received - amount_refunded, 0)

    print("amount received : ", amount_received)
    print("amount refunded : ", amount_refunded)
    print("remaining amount : ", remaining)

    if remaining <= 0:
        return Response({"detail": "Payment is already fully refunded."}, status=status.HTTP_400_BAD_REQUEST)

    # If client didn’t pass amount -> refund remaining (full refund)
    if amount is None:
        amount = remaining
    else:
        try:
            amount = Decimal(amount) * 100  # convert to minor units
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"detail": "amount must be an integer (minor units)."}, status=status.HTTP_400_BAD_REQUEST)
        if amount < 0 or amount > remaining:
            return Response({"detail": f"amount must be between 1 and {remaining}."}, status=status.HTTP_400_BAD_REQUEST)

    print("final original amount is : ", amount)

    # 4) Create refund (to original payment method)
    # Idempotency prevents double refunds if the request repeats
    idempotency_key = request.headers.get("Idempotency-Key") or f"refund-booking-{booking_id}-{uuid.uuid4()}"

    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,   # you can also pass charge=...; PI is fine
            amount=amount,
            reason=reason,
            metadata={
                "booking_id": str(booking_id),
                # "environment": "prod",  # or "dev"
                "environment": "dev",  # or "prod"

            },
            idempotency_key=idempotency_key,
        )
    except stripe.error.CardError as e:
        return Response({"detail": "Card error while refunding.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.InvalidRequestError as e:
        return Response({"detail": "Invalid request to Stripe.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.APIConnectionError as e:
        return Response({"detail": "Network error contacting Stripe.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except stripe.error.StripeError as e:
        return Response({"detail": "Stripe error.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    print(f"{amount} refund successfully !!!")
    # 5) Update booking status locally:
    # Safer pattern: mark "refund_pending" now and let your webhook set "refunded" once Stripe confirms.
    booking.cancellation_status = "approved"
    booking.cancellation_request = False
    booking.refund_id = refund.id
    # booking.refunded_amount = Decimal(amount) / 100  # minor units → টাকা
    booking.refunded_amount = amount
    booking.refund_reason = reason or ""
    booking.save(update_fields=["cancellation_status", "cancellation_request",
                                "refund_id", "refunded_amount", "refund_reason"])
    
    traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
    print("sending booking cancellation request approval email from admin to traveller")
    booking_cancellation_request_approval_email_from_admin_to_traveller_task(booking_id, traveller_dashboard_url)
    print("booking cancellation request approval email sent successfully.")
                                
    return Response({
        "detail": "Refund initiated.",
        "booking_id": booking_id,
        "payment_intent": payment_intent_id,
        "refund": {
            "id": refund.id,
            "status": refund.status,  # e.g., 'succeeded' or 'pending'
            "amount": refund.amount,
            "currency": refund.currency,
            "reason": refund.reason,
        }
    }, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
def denyCancellationRequest(request, pk):
    try:
        tour_booking = TourBooking.objects.get(id=pk)
        if tour_booking.cancellation_request and tour_booking.cancellation_status == 'reviewing':
            # Simply reset the request fields without changing the selected_date
            tour_booking.cancellation_request = False
            tour_booking.cancellation_status = 'denied'
            tour_booking.refund_percentage = Decimal('0.00')
            tour_booking.requested_refund_amount = Decimal('0.00')
            tour_booking.refund_status = None
            tour_booking.cancellation_denied_count += 1  # Increment the denial count
            tour_booking.save()
            if tour_booking.cancellation_denied_count >= 3:
                tour_booking.cancellation_eligible = False
                tour_booking.save()
            response_data = {
                "booking_id": pk,
                "cancellation_request" : False,
                "cancellation_status": "denied",
                "refund_percentage": "0.00%",
                "requested_refund_amount": "0.00",
                "refund_status": tour_booking.refund_status,
                "cancellation_denied_count": tour_booking.cancellation_denied_count
            }
            traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
            booking_id = tour_booking.id
            print("sending booking cancellation request deny email from admin to traveller")
            send_booking_cancellation_request_deny_email_to_traveller_task(booking_id, traveller_dashboard_url)
            print("date change request deny email sent successfully.")
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No pending cancellation request to deny.'}, status=status.HTTP_400_BAD_REQUEST)
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {pk} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteTourBooking(request, pk):
    try:
        tour_booking = TourBooking.objects.get(pk=pk)
        tour_booking.delete()
      
        return Response({'detail': f'Tour Booking  id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Tour Booking id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def ManualCancellationOfBookingByAdmin(request, pk):
    data = request.data
    print("data :", data)
    cancellation_reason = data.get('cancellation_reason')
    is_applied_cancellation_policy = data.get('is_applied_cancellation_policy', False)

    try:
        # Fetch the booking object based on the provided booking ID (pk)
        tour_booking = TourBooking.objects.get(id=pk)
        tour_booking_id = tour_booking.id

        # 🧩 NEW PART — Invalidate Stripe Session
        try:
            if tour_booking.payment_url:
                # payment_url থেকে session_id বের করা
                # session_id থাকে এরকম: https://checkout.stripe.com/c/pay/cs_test_a1B2C3...
                url = tour_booking.payment_url
                print('\n')
                print("payment url is :", url)
                # fragment বাদ দিয়ে শুধু path বের করা
                path = urlparse(url).path
                print('\n')
                print("path is :", path)
                # এখন শেষের অংশটা নাও
                session_id = path.split("/")[-1]
                print('\n')
                print(session_id)
                stripe.checkout.Session.expire(session_id)
                print(f"✅ Stripe session expired for booking ID {tour_booking.id}")
        except Exception as e:
            print(f"⚠️ Failed to expire Stripe session: {e}")

        # Proceed only if booking is not already cancelled, when cancelled its cancellation_status will be 'approved'. 
        if tour_booking.cancellation_status != 'approved':
            # Reset cancellation-related fields
            tour_booking.cancellation_request = False
            tour_booking.cancellation_status = 'approved'
            tour_booking.cancellation_eligible = False  # Disallow future cancellations
            tour_booking.save()

            # initialize default values for refund and policy-related data
            refund_percentage = Decimal('0.00')
            refunded_amount = Decimal('0.00')
            simple_cutoff_hours = None
            applied_penalty_rule_id = None
            cutoff_hours = None
            all_penalty_rules = []
            published_policy_list = []
            cancellation_policy = {}
            
            # CASE 1: If booking is not paid yet (e.g., pending), we will not send any mail to him.
            # ai case e 'not equals to paid' maane only pending obosthay jodi thaake, cause onnanno status gulo jemon refunded, partially refunded agula thakle cancel korar button e show korbe na front end theke. 
            if tour_booking.status != 'paid':
                # If the booking was never paid, no refund applicable
                tour_booking.status = "cancelled by admin"
                tour_booking.cancellation_reason = cancellation_reason
                tour_booking.manually_cancelled_by_admin = True # marking kora hoise j ai booking ta manually cancelled by admin
                tour_booking.save()
                
                
                return Response({
                    "detail" : "Manually cancelled the booking by admin. Since the booking was not paid, no refund is applicable.",
                    "booking_id": tour_booking_id,
                    "status": tour_booking.status,
                    "cancellation_status": tour_booking.cancellation_status,
                    "cancellation_reason": tour_booking.cancellation_reason
                }, status=status.HTTP_200_OK)
            
            # CASE 2: If booking was paid and admin chose to apply the cancellation policy
            if is_applied_cancellation_policy == True:
                # Retrieve tour and its cancellation policies
                # Apply the cancellation policy logic to determine refund_percentage and requested_refund_amount
                tour = tour_booking.tour
                all_cancellation_policies = tour.cancellation_policies_list.all()
                applied_policy = all_cancellation_policies.filter(default_policy=True).first()

                # ⚠️ Potential issue: If no default policy exists, return error
                if not applied_policy:
                    return Response({'error': "No default cancellation policy found for this tour."}, status=status.HTTP_400_BAD_REQUEST)

                policy_type = applied_policy.policy_type
                print("applied_policy id :", applied_policy.id)
                print("policy_type :", policy_type)
                print('\n')

                # Current system local time
                now_utc = timezone.now()
                localtime = timezone.localtime(now_utc)

                # custom event datetime (00:00:00 of the event day)
                custom_event_datetime = datetime.combine(tour_booking.selected_date, time.min)
                custom_event_datetime = timezone.make_aware(custom_event_datetime, timezone.get_current_timezone())
                print("custom_event_datetime:", custom_event_datetime)
                custom_diff = custom_event_datetime - localtime
                custom_total_seconds = int(custom_diff.total_seconds())
                print("custom_total_seconds:", custom_total_seconds)

                # Apply logic based on cancellation policy type
                if policy_type == "simple":
                    print('\n')
                    print("enters into simple policy type")
                    simple_cutoff_hours = applied_policy.simple_cutoff_hours
                    simple_cutoff_seconds = simple_cutoff_hours * 60 * 60
                    print("simple cutoff seconds", simple_cutoff_seconds)
                    print('\n')
                    
                    # If cancellation made before cutoff period → Full refund
                    if custom_total_seconds > simple_cutoff_seconds:
                        refund_percentage = Decimal('100.00')
                        refunded_amount = tour_booking.total_price
                        # refund_eligible = True
                        rule_range = f"Cancellation fee of 100% is charged if cancelled {simple_cutoff_hours} hours or less before the event, otherwise 0% will be charged."
                        cancellation_policy["type"] = policy_type
                        cancellation_policy["range"] = rule_range
                        cancellation_policy["refund_percentage"] = Decimal('100.00')
                        published_policy_list.append(
                            cancellation_policy
                        )
                    
                    # If cancellation made within cutoff → No refund
                    if custom_total_seconds <= simple_cutoff_seconds:
                        rule_range = f"Cancellation fee of 100% is charged if cancelled {simple_cutoff_hours} hours or less before the event, otherwise 0% will be charged."
                        cancellation_policy["type"] = policy_type
                        cancellation_policy["range"] = rule_range
                        cancellation_policy["refund_percentage"] = Decimal('0.00')
                        published_policy_list.append(
                            cancellation_policy
                        )

                elif policy_type == "full_refund":
                    # Always refund 100% if cancellation occurs before event start
                    print('\n')
                    print("enters into full_refund policy type")
                    if custom_total_seconds > 0:
                        refund_percentage = Decimal('100.00')
                        refunded_amount = tour_booking.total_price
                        # refund_eligible = True
                        rule_range = f"Cancellation fee of 0.00% is charged if cancelled any time before starting the event."
                        cancellation_policy["type"] = policy_type
                        cancellation_policy["range"] = rule_range
                        cancellation_policy["refund_percentage"] = refund_percentage
                        published_policy_list.append(
                            cancellation_policy
                        )

                elif policy_type == "non_refundable":
                    print('\n')
                    print("enters into non refundable policy type")
                    # No refund in any case
                    rule_range = f"Cancellation fee of 100.00% is charged if cancelled the booking."
                    cancellation_policy["type"] = policy_type
                    cancellation_policy["range"] = rule_range
                    cancellation_policy["refund_percentage"] = Decimal("0.00")
                    published_policy_list.append(
                        cancellation_policy
                    )

                elif policy_type == "advanced":
                    print('\n')
                    print("enters into advanced policy type")
                    # Advanced policies have multiple cutoff ranges (penalty rules)
                    all_penalty_rules = applied_policy.penalty_rules.all().order_by('cutoff_hours')
                    print('\n')
                    for rule in all_penalty_rules:
                        print(f"rule id {rule.id} cutoff hours : {rule.cutoff_hours}" )
                    print('\n')

                    # If event date is already passed → No refund
                    if custom_total_seconds < 0:
                        refund_percentage = Decimal('0.00')
                        refunded_amount = Decimal('0.00')
                        
                    elif all_penalty_rules.exists():
                        # Get the largest cutoff (furthest in advance)
                        largest_threshold_seconds = all_penalty_rules.last().cutoff_hours * 60 * 60
                        print("largest_threshold_seconds :", largest_threshold_seconds)
                        
                        # If cancelled earlier than the max cutoff → full refund
                        if custom_total_seconds > largest_threshold_seconds:
                            refund_percentage = Decimal('100.00')
                            refunded_amount = tour_booking.total_price
                        else:
                            # Otherwise, loop through rules to find matching range
                            for rule in all_penalty_rules:
                                applied_penalty_rule_id = rule.id
                                cutoff_hours = rule.cutoff_hours
                                cutoff_seconds = cutoff_hours * 60 * 60

                                if custom_total_seconds <= cutoff_seconds:
                                    print("applied rule id : ", rule.id)
                                    print("custom total seconds : ", custom_total_seconds)
                                    print("cutoff_seconds : ", cutoff_seconds)
                                    cancellation_percentage = rule.percentage
                                    print("cancellation percentage : ", cancellation_percentage)
                                    refund_percentage = Decimal('100.00') - cancellation_percentage
                                    print("refund percentage : ", refund_percentage)
                                    refunded_amount = (tour_booking.total_price * refund_percentage) / Decimal('100.00')
                                    break
                
                else:
                    # ⚠️ Invalid or unsupported policy type
                    return Response({"error": "Invalid policy_type"}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                # If no policy is applied → full refund by default
                refund_percentage = Decimal('100.00')
                refunded_amount = tour_booking.total_price
            
            # Save refund-related info to booking
            print('\n')
            print(f"Final refund_percentage: {refund_percentage}, refunded_amount: {refunded_amount}")
            tour_booking.refund_percentage = refund_percentage
            tour_booking.requested_refund_amount = refunded_amount
            tour_booking.refund_status = 'pending' if refunded_amount > 0 else None
            tour_booking.cancellation_reason = cancellation_reason
            tour_booking.save()
            
            # CASE 3: If refund amount is zero → cancel without refund
            amount = tour_booking.requested_refund_amount
            print('\n')
            print("final requested refund amount is : ", amount)
            if amount == 0:
                tour_booking.manually_cancelled_by_admin = True
                tour_booking.status = "cancelled without refund"
                tour_booking.refund_status = "cancelled without refund"
                tour_booking.cancellation_status = "approved"
                tour_booking.cancellation_request = False
                tour_booking.cancellation_eligible = False
                tour_booking.save(update_fields=["manually_cancelled_by_admin","status", "refund_status", "cancellation_status", "cancellation_request", "cancellation_eligible"])
                
                # Send notification email to traveller
                traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
                print("sending booking cancellation request approval email from admin to traveller")
                send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin_task(tour_booking_id, traveller_dashboard_url)
                print("booking cancellation request approval email sent successfully.")
                
                # Return response confirming cancellation without refund
                response_data = {
                    "detail" : "Manually cancelled the booking by admin, and Booking cancelled without refund as the refundable amount is 0.",
                    "booking_id": tour_booking_id,
                    "refund_percentage": refund_percentage,
                    "refunded_amount": refunded_amount,
                    "status": tour_booking.status,
                    "refund_status": tour_booking.refund_status,
                    "cancellation_status": tour_booking.cancellation_status,
                    "published_policy_list": published_policy_list
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            # CASE 4: If refund amount > 0 → proceed with Stripe refund            
            # refund through payment gateway if any amount to refund
            else:
                payment_intent_id = getattr(tour_booking, "payment_key", None)
                print("payment_intent_id :", payment_intent_id)
                
                # ⚠️ Handle missing Stripe payment key
                if not payment_intent_id:
                    return Response({"detail": "No Stripe payment key (Payment Intent ID) stored on booking."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Retrieve payment intent from Stripe
                try:
                    pi = stripe.PaymentIntent.retrieve(payment_intent_id)
                except stripe.error.StripeError as e:
                    return Response({"detail": "Failed to retrieve Payment Intent from Stripe.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

                # Determine remaining refundable amount (in minor units)
                amount_received = int(pi.get("amount_received") or 0)
                amount_refunded = int(pi.get("amount_refunded") or 0)
                remaining = max(amount_received - amount_refunded, 0)

                print("amount received : ", amount_received)
                print("amount refunded : ", amount_refunded)
                print("remaining amount : ", remaining)

                if remaining <= 0:
                    return Response({"detail": "Payment is already fully refunded."}, status=status.HTTP_400_BAD_REQUEST)

                # If client didn’t pass amount -> refund remaining (full refund)
                if amount is None:
                    amount = remaining
                else:
                    try:
                        # Convert refund amount to minor currency units (cents)
                        amount = Decimal(amount) * 100  # convert to minor units
                        amount = int(amount)
                    except (TypeError, ValueError):
                        return Response({"detail": "amount must be an integer (minor units)."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if amount < 0 or amount > remaining:
                        return Response({"detail": f"amount must be between 1 and {remaining}."}, status=status.HTTP_400_BAD_REQUEST)

                print("final original amount is : ", amount)

                # Generate unique idempotency key for Stripe refund request
                # Idempotency prevents double refunds if the request repeats
                idempotency_key = request.headers.get("Idempotency-Key") or f"refund-booking-{tour_booking_id}-{uuid.uuid4()}"
                
                # Attempt refund through Stripe API
                try:
                    refund = stripe.Refund.create(
                        payment_intent=payment_intent_id,   # you can also pass charge=...; PI is fine
                        amount=amount,
                        # reason="requested_by_customer",
                        metadata={
                            "booking_id": str(tour_booking_id),
                            # "environment": "prod",  # or "dev"
                            "environment": "dev",  # or "prod"
                            "cancellation_reason": cancellation_reason or "Manually cancelled by admin"
                        },
                        idempotency_key=idempotency_key,
                    )
                except stripe.error.CardError as e:
                    return Response({"detail": "Card error while refunding.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except stripe.error.InvalidRequestError as e:
                    return Response({"detail": "Invalid request to Stripe.", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except stripe.error.APIConnectionError as e:
                    return Response({"detail": "Network error contacting Stripe.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
                except stripe.error.StripeError as e:
                    return Response({"detail": "Stripe error.", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

                print(f"{amount} refund successfully !!!")
                # 5) Update booking status locally:
                tour_booking.manually_cancelled_by_admin = True
                tour_booking.cancellation_status = "approved"
                tour_booking.cancellation_request = False
                tour_booking.refund_id = refund.id
                # tour_booking.refunded_amount = Decimal(amount) / 100
                tour_booking.refunded_amount = amount
                tour_booking.refund_reason = "Manually cancelled by admin"
                tour_booking.save(update_fields=["manually_cancelled_by_admin","cancellation_status", "cancellation_request",
                                            "refund_id", "refunded_amount", "refund_reason"])
                
                # Send refund confirmation email to traveller
                traveller_dashboard_url = settings.TRAVELLER_DASHBOARD_URL
                print("sending manually booking cancellation,  email from admin to traveller")
                send_email_from_admin_to_traveller_when_manually_cancelled_booking_by_admin_task(tour_booking_id, traveller_dashboard_url)
                print("manually booking cancellation email sent successfully.")
                
                # Return success response with refund details
                response_data = {
                    "detail" : "Manually cancelled the booking by admin, and Booking cancelled with refund as the refundable amount is more than 0.",
                    "booking_id": tour_booking_id,
                    "refund_percentage": refund_percentage,
                    "refunded_amount": refunded_amount,
                    "status": tour_booking.status,
                    "refund_status": tour_booking.refund_status,
                    "cancellation_status": tour_booking.cancellation_status,
                    "payment_intent": payment_intent_id,
                    "refund": {
                        "id": refund.id,
                        "status": refund.status,  # e.g., 'succeeded' or 'pending'
                        "amount": Decimal(refund.amount) / 100,
                        "currency": refund.currency,
                        "reason": refund.reason,
                    },
                    "published_policy_list": published_policy_list
                }
                return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            # If booking already cancelled, return message
            return Response({'error': 'Booking is already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle case where booking ID does not exist
    except ObjectDoesNotExist:
        return Response({'error': f"Booking id {pk} doesn't exists."}, status=status.HTTP_400_BAD_REQUEST)
