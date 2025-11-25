from decimal import Decimal
import json
import os
from time import time
import uuid
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from authentication.models import User
from payments.models import Payment, Traveller
from payments.serializers.payment_serializers import PaymentSerializer
from payments.tasks import send_booking_confirmation_email_to_traveller_task, send_payment_confirmation_email_to_traveller_task
from tour.tasks import booking_cancellation_request_approval_email_from_admin_to_traveller_task
from payments.utils import generate_invoice_id
from tour.models import TourBooking
from tour.serializers.tour_booking_serializers import TourBookingSerializer
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser  # refund should be admin-only
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from kombu.exceptions import OperationalError
from urllib.parse import urlparse

stripe.api_key = settings.STRIPE_SECRET_KEY


PAID_STATUSES = {"paid"}  # adjust to your project

@api_view(["POST"])
def refundBalanceFromStripeToTraveller(request, pk):
    """
    Refund a paid booking back to the original card.
    Request (JSON):
      {
        "amount":  null or integer minor units (e.g., 5000 for 50.00), optional -> defaults to full remaining,
        "reason":  "requested_by_customer" | "duplicate" | "fraudulent" (optional)
      }
    """
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
@csrf_exempt
def stripe_webhook(request):
    print('\n')
    print("hello from stripe webhook")
    print('\n')


    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', None)
    try:
        print("Constructing event from payload and signature header.")
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
        print("Event constructed successfully:")
    except stripe.error.SignatureVerificationError:
        print("⚠️ Invalid signature. Event not verified.")
        return HttpResponse(status=400)

    # ✅ Safe event handling
    event_type = event.get("type")
    print(f"Stripe event type: {event_type}")

    dashboard_url = settings.TRAVELLER_DASHBOARD_URL

    # ========== Handle Important Events ==========
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        tour_booking_id = metadata.get('tour_booking_id')
        success_url = metadata.get('success_url')
        payment_intent_id = session.get("payment_intent")
        print("tour_booking_id : ", tour_booking_id)
        print("payment_intent_id : ", payment_intent_id)

        tour_booking = TourBooking.objects.filter(id=tour_booking_id).first()
        if not tour_booking:
            print("❌ No booking found for this tour_booking_id")
        else:
            booking_id = tour_booking.booking_id
            tour_name = tour_booking.tour.name 
            traveller_email = tour_booking.user.email
            traveller_phone = tour_booking.traveller.phone
            total_price = tour_booking.total_price
            participants = tour_booking.total_participants
            selected_date = tour_booking.selected_date
            selected_time = tour_booking.selected_time if tour_booking.selected_time is not None else None
            payment_intent_id = payment_intent_id

        # ✅ এখানে PaymentIntent এ metadata আপডেট করে দাও
        try:
            stripe.PaymentIntent.modify(
                payment_intent_id,
                metadata={
                    'tour_booking_id': booking_id,
                    'tour_name': tour_name,
                    'traveller_email': traveller_email,
                    'traveller_phone': traveller_phone,
                    'total_price': total_price,
                    'participants': participants,
                    'selected_date': selected_date,
                    'selected_time': selected_time,
                    "payment_intent_id": payment_intent_id
                }
            )
            print("✅ PaymentIntent metadata updated successfully.")
        except Exception as e:
            print("❌ Failed to update PaymentIntent metadata:", str(e))

        # ========== Handle Booking & Payment ==========
        try:
            tour_booking = TourBooking.objects.get(id=tour_booking_id)
            print("✅ tour booking found.")
        except TourBooking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # catch traveller instance
        user = tour_booking.user
        traveller = tour_booking.traveller
        print("user:", user, "| traveller:", traveller)

        # getting payment_key from stripe
        payment_key = payment_intent_id or None  
        payment_url = tour_booking.payment_url
        session_id = session['id'] if session else None

        # generating invoice_id from custom function
        invoice_id = generate_invoice_id(tour_booking.selected_date, tour_booking_id)
        print("invoice_id is :", invoice_id )

        payment_data = {
            "company": tour_booking.company.id,
            "invoice_id": invoice_id,
            "tour_booking": tour_booking.id,
            "user": user.id,
            "traveller": traveller.id,
            "tour": tour_booking.tour.id,
            "total_price": tour_booking.total_price,
            "payment_method": "stripe",
            "payment_status": "paid",
            "payWithCash": False,
            "payWithStripe": True,
            "payment_key": payment_key,
            "payment_url": payment_url,
            "session_id": session_id,
            "created_by": user.id,
            "updated_by": user.id,
        }
        print("Payment data created successfully.")

        # --- Idempotency: check existing payment
        existing_payment = None
        if payment_key:
            existing_payment = Payment.objects.filter(payment_key=payment_key).first()

        if existing_payment:
            payment = existing_payment
            print("Payment already exists for key=%s", payment_key)
            # Ensure booking linked
            print("already in existing payment")
            if tour_booking.payment.id != payment.id:
            # if tour_booking.payment == None:
                print("inside the existing payment")
                tour_booking.payment = payment
                tour_booking.status = "paid"
                tour_booking.payment_key = payment_key
                tour_booking.save(update_fields=["payment", "status", "payment_key"])
        else:
            try:
                with transaction.atomic():
                    payment_serializer = PaymentSerializer(data=payment_data)
                    if payment_serializer.is_valid():
                        payment = payment_serializer.save()
                        print("Payment created for booking id", tour_booking_id)
                        # Update booking
                        tour_booking.payment = payment
                        tour_booking.status = "paid"
                        tour_booking.payment_key = payment_key
                        tour_booking.save(
                            update_fields=["payment", "status", "payment_key"]
                        )
                    else:
                        print("Payment serializer errors: %s", payment_serializer.errors)
                        return Response(
                            {"message": "Ignored duplicate/invalid payment"},
                            status=200,  # avoid Stripe retries
                        )
            except Exception as e:
                print("DB error while creating payment: ", e)
                return Response(
                    {"message": "Server error logged"}, status=200
                )
        
        # --- Celery tasks (safe)
        try:
            tour_booking_id = tour_booking.id
            print("tour booking id : ", tour_booking_id)
            print(type(tour_booking_id))
            payment_id = payment.id
            traveller_id = traveller.id

            def trigger_tasks():
                print("triggered task from transaction.on_commit() ")
                send_booking_confirmation_email_to_traveller_task.delay(
                    tour_booking_id, payment_id, traveller_id, dashboard_url
                )
                send_payment_confirmation_email_to_traveller_task.delay(
                    tour_booking_id, payment_id, traveller_id, dashboard_url
                )
                print("✅ Celery tasks scheduled after commit for booking:", tour_booking_id)

            transaction.on_commit(trigger_tasks)
        except OperationalError as e:
            print("Celery broker error: ", e)
            # Optional fallback: save to DB for later retry
            # PendingTask.objects.create(type="send_email", payload={...})

        return Response({"message": "payment processed successfully and email sent"}, status=200)

    elif event_type == 'checkout.session.expired':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        tour_booking_id = metadata.get('tour_booking_id')
        print("tour_booking_id from expired session: ", tour_booking_id)

        if not tour_booking_id:
            print("❌ No tour_booking_id in session metadata")
            return Response({"status": "no tour_booking_id in session metadata"}, status=200)

        try:
            booking = TourBooking.objects.get(id=tour_booking_id)
        except TourBooking.DoesNotExist:
            print("❌ No booking found for this expired session")
            return Response({"status": "no booking found for this expired session"}, status=200)

        return Response({"status": "checkout session expired handled."}, status=200)
    
    elif event_type == 'payment_intent.succeeded':
        intent = event['data']['object']
        print("✅ Payment succeeded, intent ID:", intent['id'])
        # এখানে তুমি চাইলে payment log রাখতে পারো
        return Response({"status": "payment intent succeeded."}, status=200)

    elif event_type == 'payment_intent.payment_failed':
        intent = event['data']['object']
        print("❌ Payment failed, intent ID:", intent['id'])
        # failed payment log করে রাখো
        return Response({"status": "payment intent failed."}, status=200)

    elif event_type == 'charge.succeeded':
        charge = event['data']['object']
        print("💰 Charge succeeded:", charge['id'])
        return Response({"status": "charge succeeded."}, status=200)

    elif event_type == 'charge.failed':
        charge = event['data']['object']
        print("❌ Charge failed:", charge['id'])
        return Response({"status": "charge failed."}, status=200)

    elif event_type == "refund.created":
        refund = event["data"]["object"]
        print("🔄 Refund created:", refund["id"])
        
        # Extract the payment_intent from refund data
        payment_intent_id = refund.get("payment_intent")
    
        # Find the corresponding booking using payment_intent_id
        try:
            booking = TourBooking.objects.get(payment_key=payment_intent_id)
        except TourBooking.DoesNotExist:
            print("❌ No booking found for this refund")
            return HttpResponse(status=404)
        
        print("Refund details:", refund)
        
        # Update booking fields related to refund creation
        if booking.status not in ["refunded", "partial_refund"]:
            booking.status = "refund_pending"
            booking.refund_id = refund["id"]
            booking.refunded_amount = refund.get("amount", 0) / 100
            booking.refund_reason = refund.get("reason", "")
            booking.save(update_fields=["status", "refund_id", "refunded_amount", "refund_reason"])
            print("✅ Booking updated → refund_pending")
        else:
            print("ℹ️ Booking already refunded or partially refunded — skipping refund_pending update.")
        return Response({"status": "refund created."}, status=200)

    elif event_type == "charge.refunded":
        refund = event["data"]["object"]
        print('\n')
        print("refund from charge.refunded :", refund)
        print("💸 Charge refunded:", refund["id"])
        print('\n')
        payment_intent_id = refund.get("payment_intent")

        try:
            booking = TourBooking.objects.get(payment_key=payment_intent_id)
        except TourBooking.DoesNotExist:
            print("❌ No booking found for charge.refunded")
            return HttpResponse(status=404)
        main_amount = int(refund.get("amount", 0))
        refunded_amount = refund.get("amount_refunded", 0)
        remaining = main_amount - refunded_amount
        print("main amount :", main_amount)
        print("refunded amount :", refunded_amount)
        print("remaining amount :", remaining)

        if remaining == 0:
            booking.status = "refunded"
            booking.refund_status = "refunded"
            booking.refund_reason = refund.get("reason", "")

            booking.save(update_fields=["status", "refund_status", "refund_reason"]) 
            print("✅ Booking updated → refunded")

        else:
            booking.status = "partial_refund"
            booking.refund_status = "partial_refund"
            booking.refund_reason = refund.get("reason", "")

            booking.save(update_fields=["status", "refund_status", "refund_reason"]) 
            print("✅ Booking updated → partial_refund")
        return Response({"status": "charge refunded."}, status=200)

    elif event_type == "refund.updated":
        refund = event["data"]["object"]
        print('\n')
        print("refund from refund.updated :", refund)
        print("✏️ Refund updated:", refund["id"])
        print('\n')
        # চাইলে এখানে log update করতে পারো (status change হলে)
        return Response({"status": "refund updated."}, status=200)

    elif event_type == "charge.refund.updated":
        charge = event["data"]["object"]
        print('\n')
        print("charge from charge.refund.updated :", charge)
        print("🔁 Charge refund updated:", charge["id"])
        print('\n')
        # future use: log / notify
        return Response({"status": "charge refund updated."}, status=200)


    else:
        # অন্যান্য event শুধু log করো
        print(f"Unhandled Stripe event type: {event_type}")
        return HttpResponse(status=200)  # সবসময় OK return করতে হবে

