import re
import requests


def upload_to_cloudflare(thumbnail_image):
    """
    Upload an image to Cloudflare and return the URL of the uploaded image.
    """
    endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
    headers = {
        'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
    }
    files = {
        'file': thumbnail_image.file
    }
    print("creating response from Cloudflare")
    response = requests.post(endpoint, headers=headers, files=files)
    print("Response status code:", response.status_code)
    response.raise_for_status()
    json_data = response.json()
    variants = json_data.get('result', {}).get('variants', [])
    if variants:
        cloudflare_image = variants[0]  # Use the first variant URL
        print("Cloudflare image URL from response:", cloudflare_image)
        return cloudflare_image
    else:
        print("No variants found in the Cloudflare response")
        return None
    
def generate_slug(name):
    clean_name = re.sub(r'[^A-Za-z0-9\s-]', '-', name)

    # Replace spaces with hyphens
    clean_name = re.sub(r'\s+', '-', clean_name)

    # Convert to lowercase
    clean_name = clean_name.lower()

    # Replace multiple consecutive hyphens with a single hyphen
    clean_name = re.sub(r'-{2,}', '-', clean_name)

    # Strip leading and trailing hyphens
    clean_name = clean_name.strip('-')

    slug = clean_name
    return slug

def reformed_head_or_name(given_string):
    # lower case
    lower_case = given_string.lower()
    
    # removing with guide or without guide
    cleaned = re.sub(r'\b(without guide|with guide)\b', '', lower_case)

    # convert extra spaces into a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # converting space into '-' but without replacing '(' or ')'
    cleaned = re.sub(r'\s', '-', cleaned)

    return cleaned


# @api_view(['POST'])
# @csrf_exempt
# def stripe_webhook(request):
#     print('\n')
#     print("hello from stripe webhook")
#     print('\n')


#     # Always initialize
#     tour_booking_id = None
#     session = None

#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request method for stripe webhook'}, status=405)

#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', None)
#     try:
#         print("Constructing event from payload and signature header.")
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
#         )
#         print("Event constructed successfully:")
#     except stripe.error.SignatureVerificationError:
#         print("⚠️ Invalid signature. Event not verified.")
#         return HttpResponse(status=400)

#     # ✅ Safe event handling
#     event_type = event.get("type")
#     print(f"Stripe event type: {event_type}")

#     # ========== Handle Important Events ==========
#     if event_type == 'checkout.session.completed':
#         session = event['data']['object']
#         metadata = session.get('metadata', {})
#         tour_booking_id = metadata.get('tour_booking_id')
#         success_url = metadata.get('success_url')
#         payment_intent_id = session.get('payment_intent')
#         print("tour_booking_id : ", tour_booking_id)
#         print("payment_intent_id : ", payment_intent_id)

#         tour_booking = TourBooking.objects.filter(id=tour_booking_id).first()
#         if not tour_booking:
#             print("❌ No booking found for this tour_booking_id")
#         else:
#             booking_id = tour_booking.booking_id
#             tour_name = tour_booking.tour.name 
#             traveller_email = tour_booking.user.email
#             traveller_phone = tour_booking.traveller.phone
#             total_price = tour_booking.total_price
#             participants = tour_booking.total_participants
#             selected_date = tour_booking.selected_date
#             selected_time = tour_booking.selected_time
#             payment_intent_id = payment_intent_id

#         # ✅ এখানে PaymentIntent এ metadata আপডেট করে দাও
#         try:
#             stripe.PaymentIntent.modify(
#                 payment_intent_id,
#                 metadata={
#                     'tour_booking_id': booking_id,
#                     'tour_name': tour_name,
#                     'traveller_email': traveller_email,
#                     'traveller_phone': traveller_phone,
#                     'total_price': total_price,
#                     'participants': participants,
#                     'selected_date': selected_date,
#                     'selected_time': selected_time,
#                     "payment_intent_id": payment_intent_id
#                 }
#             )
#             print("✅ PaymentIntent metadata updated successfully.")
#         except Exception as e:
#             print("❌ Failed to update PaymentIntent metadata:", str(e))

#     elif event_type == 'payment_intent.succeeded':
#         intent = event['data']['object']
#         print("✅ Payment succeeded, intent ID:", intent['id'])
#         # এখানে তুমি চাইলে payment log রাখতে পারো

#     elif event_type == 'payment_intent.payment_failed':
#         intent = event['data']['object']
#         print("❌ Payment failed, intent ID:", intent['id'])
#         # failed payment log করে রাখো

#     elif event_type == 'charge.succeeded':
#         charge = event['data']['object']
#         print("💰 Charge succeeded:", charge['id'])

#     elif event_type == 'charge.failed':
#         charge = event['data']['object']
#         print("❌ Charge failed:", charge['id'])

#     elif event_type == "refund.created":
#         refund = event["data"]["object"]
#         print("🔄 Refund created:", refund["id"])
#         payment_intent_id = refund.get("payment_intent")

#         # TourBooking খুঁজে বের করা
#         try:
#             booking = TourBooking.objects.get(payment_key=payment_intent_id)
#         except TourBooking.DoesNotExist:
#             print("❌ No booking found for this refund")
#             return HttpResponse(status=404)
        
#         print("refund : ", refund)

#         booking.status = "refund_pending"
#         booking.refund_id = refund["id"]
#         booking.refunded_amount = refund.get("amount", 0) / 100  # stripe minor units → টাকা
#         booking.refund_reason = refund.get("reason", "")
#         booking.save(update_fields=["status", "refund_id", "refunded_amount", "refund_reason"])
#         print("✅ Booking updated → refund_pending")

#     elif event_type == "charge.refunded":
#         refund = event["data"]["object"]
#         print('\n')
#         print("refund from charge.refunded :", refund)
#         print("💸 Charge refunded:", refund["id"])
#         print('\n')
#         payment_intent_id = refund.get("payment_intent")

#         try:
#             booking = TourBooking.objects.get(payment_key=payment_intent_id)
#         except TourBooking.DoesNotExist:
#             print("❌ No booking found for charge.refunded")
#             return HttpResponse(status=404)
#         main_amount = int(refund.get("amount", 0))
#         refunded_amount = refund.get("amount_refunded", 0)
#         remaining = main_amount - refunded_amount
#         print("main amount :", main_amount)
#         print("refunded amount :", refunded_amount)
#         print("remaining amount :", remaining)

#         if remaining == 0:
#             booking.status = "refunded"
#             booking.refund_status = "refunded"
#             booking.save(update_fields=["status", "refund_status"]) 
#             print("✅ Booking updated → refunded")

#         else:
#             booking.status = "partial_refund"
#             booking.refund_status = "partial_refund"
#             booking.save(update_fields=["status", "refund_status"]) 
#             print("✅ Booking updated → partial_refund")

#     elif event_type == "refund.updated":
#         refund = event["data"]["object"]
#         print('\n')
#         print("refund from refund.updated :", refund)
#         print("✏️ Refund updated:", refund["id"])
#         print('\n')
#         # চাইলে এখানে log update করতে পারো (status change হলে)

#     elif event_type == "charge.refund.updated":
#         charge = event["data"]["object"]
#         print('\n')
#         print("charge from charge.refund.updated :", charge)
#         print("🔁 Charge refund updated:", charge["id"])
#         print('\n')
#         # future use: log / notify

#     else:
#         # অন্যান্য event শুধু log করো
#         print(f"Unhandled Stripe event type: {event_type}")
#         return HttpResponse(status=200)  # সবসময় OK return করতে হবে

#     # যদি booking id নাই থাকে → কিছুই update করা যাবে না
#     if not tour_booking_id:
#         return Response({"message": f"Ignored {event_type}, no booking id found"}, status=200)

#     # ========== Handle Booking & Payment ==========
#     try:
#         tour_booking = TourBooking.objects.get(id=tour_booking_id)
#         print("✅ tour booking found.")
#     except TourBooking.DoesNotExist:
#         return Response({"error": "Booking not found"}, status=404)

#     # catch traveller instance
#     user = tour_booking.user
#     traveller = tour_booking.traveller
#     print("user:", user, "| traveller:", traveller)

#     # getting payment_key from stripe
#     payment_key = payment_intent_id or None  
#     payment_url = tour_booking.payment_url
#     session_id = session['id'] if session else None

#     # generating invoice_id from custom function
#     invoice_id = generate_invoice_id(tour_booking.selected_date, tour_booking_id)
#     print("invoice_id is :", invoice_id )

#     payment_data = {
#         "invoice_id": invoice_id,
#         "tour_booking": tour_booking.id,
#         "user": user.id,
#         "traveller": traveller.id,
#         "tour": tour_booking.tour.id,
#         "total_price": tour_booking.total_price,
#         "payment_method": "stripe",
#         "payment_status": "paid",
#         "payWithCash": False,
#         "payWithStripe": True,
#         "payment_key": payment_key,
#         "payment_url": payment_url,
#         "session_id": session_id,
#         "created_by": user.id,
#         "updated_by": user.id,
#     }

#     payment_serializer = PaymentSerializer(data=payment_data)
#     if payment_serializer.is_valid():
#         payment = payment_serializer.save()
#         print("✅ payment created successfully.")
#     else:
#         print("❌ Payment serializer errors:", payment_serializer.errors)
#         return Response({"error": payment_serializer.errors}, status=400)

#     # Update Booking
#     tour_booking.payment = payment
#     tour_booking.status = "paid"
#     tour_booking.payment_key = payment_key
#     tour_booking.save()
#     print("booking updated successfully.")

#     # Send confirmation email via Celery
#     dashboard_url = settings.TRAVELLER_DASHBOARD_URL
#     # traveller_data['dashboard_url'] = dashboard_url

#     print("Triggering booking confirmation email task")
#     send_booking_confirmation_email_to_traveller_task.delay(tour_booking.id, payment.id, traveller.id, dashboard_url)
#     print("sent booking confirmation email from webhook.")
#     print('\n')

#     print("Triggering booking confirmation email task")
#     send_payment_confirmation_email_to_traveller_task.delay(tour_booking.id, payment.id, traveller.id, dashboard_url)
#     print("sent payment confirmation email from webhook.")
#     print('\n')

#     return Response({"message": "payment done successfully!"}, status=status.HTTP_201_CREATED)

