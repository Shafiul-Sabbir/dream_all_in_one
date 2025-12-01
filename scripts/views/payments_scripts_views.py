from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from payments.models import Payment, Traveller
from authentication.models import Company, User
from tour.models import Tour, TourBooking  # Importing here to avoid circular imports


@api_view(['POST'])
def load_Payment(request, company_id):
    if company_id == 3:
        file_path = 'all_json/payments/ziarah/payments_Payment_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_payment_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for payment_data in all_payment_data:
            fields = payment_data.get('fields')
            payment_id = payment_data.get('pk')
            print('\n')
            print("payment_id : ", payment_id)
            print("raw payment :", fields)
            print('\n')

            fields['old_id'] = payment_id
            fields['company'] = company_instance

            # handle foreign key for tour_booking
            tour_booking_id = fields.get('tour_booking')
            tour_booking_instance = TourBooking.objects.filter(old_id=tour_booking_id, company=company_instance).first()
            fields['tour_booking'] = tour_booking_instance

            # handle foreign key for user
            user_id = fields.get('user')
            user_instance = User.objects.filter(old_id=user_id, company=company_instance).first()
            fields['user'] = user_instance

            # handle foreign key for traveller
            traveller_id = fields.get('traveller')
            traveller_instance = Traveller.objects.filter(old_id=traveller_id, company=company_instance).first()
            fields['traveller'] = traveller_instance

            # handle foreign key for tour
            tour_id = fields.get('tour')
            tour_instance = Tour.objects.filter(old_id=tour_id, company=company_instance).first()
            fields['tour'] = tour_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None

            print("reformed payment data : ", fields)

            if not Payment.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                payment_obj = Payment.objects.create(**fields)

                print(f"Saved payment, id = {payment_obj.id}, old_id = {payment_obj.old_id}")
            else:
                print(f"payment  with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Payment successfully.'}, status=200)

@api_view(['POST'])
def load_Traveller(request, company_id):
    if company_id == 3:
        file_path = 'all_json/payments/ziarah/payments_Traveller_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_traveller_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for traveller_data in all_traveller_data:
            fields = traveller_data.get('fields')
            traveller_id = traveller_data.get('pk')
            print('\n')
            print("traveller_id : ", traveller_id)
            print("raw traveller :", fields)
            print('\n')

            fields['old_id'] = traveller_id
            fields['company'] = company_instance
            print("all ok")
            # handle foreign key for user
            user_id = fields.get('user')
            user_instance = User.objects.get(old_id=user_id, company=company_instance)
            fields['user'] = user_instance
            print("user ok")
            print("created and updated by ok")


            print("reformed traveller data : ", fields)

            if not Traveller.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                traveller_obj = Traveller.objects.create(**fields)

                print(f"Saved traveller, id = {traveller_obj.id}, old_id = {traveller_obj.old_id}")
            else:
                print(f"Traveller  with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Traveller successfully.'}, status=200)