from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from tour.models import OldAgentBooking
from authentication.models import Company, User
from tour.models import Tour, TourContentImage, DayTourPrice, AvailableDate, AvailableTime, TourItinerary, CancellationPolicy, PenaltyRules, TourBooking  # Importing here to avoid circular imports
from payments.models import Traveller, Payment

@api_view(['POST'])
def load_old_agent_bookings(request, company_id):

    if company_id == 1:
        file_path = 'all_json/tour/it/old_booking/all_data_of_agent_booking_it.json'
    elif company_id == 2:
        file_path = 'all_json/tour/uk/old_booking/all_data_of_agent_booking_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)
        all_users = []
        all_travellers = []
        all_agents = []
        all_tour_bookings = []
        all_payments = []
        all_tours = []

        # load all entries in their corresponding lists
        for entry in all_data:
            model = entry['model']

            if model == 'authentication.user':
                all_users.append(entry)
            elif model == 'payments.traveller':
                all_travellers.append(entry)
            elif model == 'member.member':
                all_agents.append(entry)
            elif model == 'tour.tourbooking':
                all_tour_bookings.append(entry)
            elif model == 'payments.payment':
                all_payments.append(entry)
            elif model == 'tour.tourcontent':
                all_tours.append(entry)

        

        print(f"Total Users: {len(all_users)}")
        print(f"Total Travellers: {len(all_travellers)}")
        print(f"Total Agents: {len(all_agents)}")
        print(f"Total Tour Bookings: {len(all_tour_bookings)}")
        print(f"Total Payments: {len(all_payments)}")
        print(f"Total Tours: {len(all_tours)}")


    for booking_data in all_tour_bookings:
        fields = booking_data.get('fields')
        booking_id = booking_data.get('pk')
        print('\n')
        print("booking_id : ", booking_id)
        print("raw booking :", fields)
        print('\n')

        fields['old_id'] = booking_data.get('pk')
        fields['company'] = company_instance

        agent_id = fields.get('agent')
        for agent in all_agents:
            if agent['pk'] == agent_id:
                agent_instance = agent.get('fields')
                # print("agent instance : ", agent_instance)
                print("agent ref no : ", agent_instance['ref_no'])
                
        print('\n')
        for user in all_users:
            if user['pk'] == agent_id:
                user_instance = user.get('fields')
                # print("user instance : ", user_instance)
                # print("username : ", user_instance.get('username'))

        full_agent_data = {**user_instance , **agent_instance}
        fields['agent'] = full_agent_data

        print("full agent data : ", full_agent_data)
        print('\n')

        tour_id = fields.get('tour')
        if tour_id is not None:
            for tour in all_tours:
                if tour['pk'] == tour_id:
                    tour_instance = tour.get('fields')
                    tour_name = tour_instance.get('name')
                    print("tour name : ", tour_instance.get('name'))
                    fields['tour'] = tour_name


        traveller_id = fields.get('traveller')
        if traveller_id is not None:
            for traveller in all_travellers:
                if traveller['pk'] == traveller_id:
                    traveller_instance = traveller.get('fields')
                    print("traveller instance : ", traveller_instance)
                    fields['traveller'] = traveller_instance

        print('\n')

        payment_id = fields.get('payment')
        print("payment id : ", payment_id)
        if payment_id is not None:
            for payment in all_payments:
                if payment['pk'] == payment_id:
                    payment_instance = payment.get('fields')
                    print("payment instance : ", payment_instance)
                    fields['payment'] = payment_instance
        else:
            for payment in all_payments:
                if payment.get('fields')['tour_booking'] == booking_id:
                    payment_instance = payment.get('fields')
                    payment_id = payment.get('pk')
                    print("payment instance : ", payment_instance)
                    print("payment id : ", payment_id)
                    fields['payment'] = payment_instance
        print('\n')
        
        json_structure_fields = json.dumps(fields, indent=4, default=str)
        print("modified booking data : ", json_structure_fields)

        if not OldAgentBooking.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
            old_agent_booking_obj = OldAgentBooking.objects.create(**fields)

            print(f"Saved old agent booking, id = {old_agent_booking_obj.id}, old_id = {old_agent_booking_obj.old_id}")
        else:
            print(f"Old Agent Booking with old_id = {fields['old_id']} already exists. Skipping.")


                    
    return Response({'message': 'Loading all Old Agent Bookings successful.'}, status=200)

@api_view(['POST'])
def load_Tour(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_Tour_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_tour_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for tour_data in all_tour_data:
            fields = tour_data.get('fields')
            tour_id = tour_data.get('pk')
            print('\n')
            print("tour_id : ", tour_id)
            print("raw tour :", fields)
            print('\n')

            fields['old_id'] = tour_id
            fields['company'] = company_instance

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

            print("reformed tour data : ", fields)

            if not Tour.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                tour_obj = Tour.objects.create(**fields)

                print(f"Saved tour, id = {tour_obj.id}, old_id = {tour_obj.old_id}")
            else:
                print(f"Tour  with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Tour successfully.'}, status=200)

@api_view(['POST'])
def load_TourContentImage(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_TourContentImage_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_tour_content_image_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for tour_content_image_data in all_tour_content_image_data:
            fields = tour_content_image_data.get('fields')
            image_id = tour_content_image_data.get('pk')
            print('\n')
            print("tour_image_id : ", image_id)
            print("raw tour content image :", fields)
            print('\n')

            fields['old_id'] = image_id
            fields['company'] = company_instance

            tour_id = fields.get('tour')
            tour_instance = Tour.objects.get(old_id=tour_id, company=company_instance)
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

            print("reformed tour content image data : ", fields)

            if not TourContentImage.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                tour_content_image_obj = TourContentImage.objects.create(**fields)

                print(f"Saved tour content image, id = {tour_content_image_obj.id}, old_id = {tour_content_image_obj.old_id}")
            else:
                print(f"Tour Content image with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Tour content images successful.'}, status=200)

@api_view(['POST'])
def load_DayTourPrice(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_DayTourPrice_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_day_tour_price_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for day_tour_price_data in all_day_tour_price_data:
            fields = day_tour_price_data.get('fields')
            day_tour_price_id = day_tour_price_data.get('pk')
            print('\n')
            print("day_tour_price_id : ", day_tour_price_id)
            print("raw day tour price :", fields)
            print('\n')

            fields['old_id'] = day_tour_price_id
            fields['company'] = company_instance

            tour_id = fields.get('tour')
            tour_instance = Tour.objects.get(old_id=tour_id, company=company_instance)
            fields['tour'] = tour_instance

            print("reformed day tour data : ", fields)

            if not DayTourPrice.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                day_tour_price_obj = DayTourPrice.objects.create(**fields)

                print(f"Saved day tour price, id = {day_tour_price_obj.id}, old_id = {day_tour_price_obj.old_id}")
            else:
                print(f"Day tour price with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Day tour price successfully.'}, status=200)

@api_view(['POST'])
def load_AvailableDate(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_AvailableDate_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_available_date_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for available_date_data in all_available_date_data:
            fields = available_date_data.get('fields')
            available_date_id = available_date_data.get('pk')
            print('\n')
            print("available_date_id : ", available_date_id)
            print("raw available date :", fields)
            print('\n')

            fields['old_id'] = available_date_id
            fields['company'] = company_instance

            day_tour_price_id = fields.get('day_tour_price')
            day_tour_price_instance = DayTourPrice.objects.get(old_id=day_tour_price_id, company=company_instance)
            fields['day_tour_price'] = day_tour_price_instance

            print("reformed available date data : ", fields)

            if not AvailableDate.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                available_date_obj = AvailableDate.objects.create(**fields)

                print(f"Saved available date, id = {available_date_obj.id}, old_id = {available_date_obj.old_id}")
            else:
                print(f"Available date with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all available date successfully.'}, status=200)

@api_view(['POST'])
def load_AvailableTime(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_AvailableTime_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_available_time_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for available_time_data in all_available_time_data:
            fields = available_time_data.get('fields')
            available_time_id = available_time_data.get('pk')
            print('\n')
            print("available_time_id : ", available_time_id)
            print("raw available time :", fields)
            print('\n')

            fields['old_id'] = available_time_id
            fields['company'] = company_instance

            day_tour_price_id = fields.get('day_tour_price')
            day_tour_price_instance = DayTourPrice.objects.get(old_id=day_tour_price_id, company=company_instance)
            fields['day_tour_price'] = day_tour_price_instance

            print("reformed available time data : ", fields)

            if not AvailableTime.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                available_time_obj = AvailableTime.objects.create(**fields)

                print(f"Saved available time, id = {available_time_obj.id}, old_id = {available_time_obj.old_id}")
            else:
                print(f"Available time with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all available time successfully.'}, status=200)

@api_view(['POST'])
def load_TourItinerary(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_TourItinerary_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_itinerary_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for itinerary_data in all_itinerary_data:
            fields = itinerary_data.get('fields')
            itinerary_id = itinerary_data.get('pk')
            print('\n')
            print("itinerary_id : ", itinerary_id)
            print("raw itinerary :", fields)
            print('\n')

            fields['old_id'] = itinerary_id
            fields['company'] = company_instance

            tour_id = fields.get('tour')
            tour_instance = Tour.objects.get(old_id=tour_id, company=company_instance)
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


            print("reformed itinerary data : ", fields)

            if not TourItinerary.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                itinerary_obj = TourItinerary.objects.create(**fields)

                print(f"Saved Itinerary, id = {itinerary_obj.id}, old_id = {itinerary_obj.old_id}")
            else:
                print(f"Itinerary with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Itinerary successfully.'}, status=200)

@api_view(['POST'])
def load_CancellationPolicy(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_CancellationPolicy_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_cancellation_policy_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for cancellation_policy_data in all_cancellation_policy_data:
            fields = cancellation_policy_data.get('fields')
            cancellation_policy_id = cancellation_policy_data.get('pk')
            print('\n')
            print("cancellation_policy_id : ", cancellation_policy_id)
            print("raw cancellation policy :", fields)
            print('\n')

            fields['old_id'] = cancellation_policy_id
            fields['company'] = company_instance

            tour_id = fields.get('tour')
            tour_instance = Tour.objects.get(old_id=tour_id, company=company_instance)
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


            print("reformed cancellation policy data : ", fields)

            if not CancellationPolicy.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                cancellation_policy_obj = CancellationPolicy.objects.create(**fields)

                print(f"Saved cancellation policy, id = {cancellation_policy_obj.id}, old_id = {cancellation_policy_obj.old_id}")
            else:
                print(f"Cancellation policy with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all cancellation policy successfully.'}, status=200)

@api_view(['POST'])
def load_PenaltyRules(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_PenaltyRules_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_penalty_rules_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for penalty_rule_data in all_penalty_rules_data:
            fields = penalty_rule_data.get('fields')
            penalty_rule_id = penalty_rule_data.get('pk')
            print('\n')
            print("penalty_rule_id : ", penalty_rule_id)
            print("raw penalty rule :", fields)
            print('\n')

            fields['old_id'] = penalty_rule_id
            fields['company'] = company_instance

            cancellation_policy_id = fields.get('cancellation_policy_list')
            cancellation_policy_instance = CancellationPolicy.objects.get(old_id=cancellation_policy_id, company=company_instance)
            fields['cancellation_policy_list'] = cancellation_policy_instance

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


            print("reformed penalty rule data : ", fields)

            if not PenaltyRules.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                penalty_rule_obj = PenaltyRules.objects.create(**fields)

                print(f"Saved penalty rule, id = {penalty_rule_obj.id}, old_id = {penalty_rule_obj.old_id}")
            else:
                print(f"Penalty rule with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all penalty rule successfully.'}, status=200)

@api_view(['POST'])
def load_TourBooking(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_TourBooking_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_tour_booking_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for tour_booking_data in all_tour_booking_data:
            fields = tour_booking_data.get('fields')
            tour_booking_id = tour_booking_data.get('pk')
            print('\n')
            print("tour_booking_id : ", tour_booking_id)
            print("raw tour booking :", fields)
            print('\n')

            fields['old_id'] = tour_booking_id
            fields['company'] = company_instance

            # handle tour field
            tour_id = fields.get('tour')
            tour_instance = Tour.objects.get(old_id=tour_id, company=company_instance)
            fields['tour'] = tour_instance

            # handle traveller field
            traveller_id = fields.get('traveller')
            traveller_instance = Traveller.objects.get(old_id=traveller_id, company=company_instance)
            fields['traveller'] = traveller_instance

            # handle user field
            user_id = fields.get('user')
            user_instance = User.objects.get(old_id=user_id, company=company_instance)
            fields['user'] = user_instance

            # handle payment field as none for now
            fields['payment'] = None

            print("reformed tour data : ", fields)

            if not TourBooking.objects.filter(old_id=fields['old_id'], company=company_instance).exists():
                tour_booking_obj = TourBooking.objects.create(**fields)

                print(f"Saved tour booking, id = {tour_booking_obj.id}, old_id = {tour_booking_obj.old_id}")
            else:
                print(f"Tour booking with old_id = {fields['old_id']} already exists. Skipping.")

    return Response({'message': 'Loading all Tour booking successfully.'}, status=200)

@api_view(['POST'])
def handle_payment_field_for_TourBooking(request, company_id):
    if company_id == 3:
        file_path = 'all_json/tour/ziarah/tour_TourBooking_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_booking_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)  

        for booking_data in all_booking_data:
            fields = booking_data.get('fields')
            booking_id = booking_data.get('pk')
            print('\n')
            print("booking_id : ", booking_id)
            print("raw booking :", fields)
            print('\n')

            # handle tour_booking field
            payment_id = fields.get('payment')
            payment_instance = Payment.objects.filter(old_id=payment_id, company=company_instance).first()

            booking_instance = TourBooking.objects.get(old_id=booking_id, company=company_instance)
            booking_instance.payment = payment_instance
            booking_instance.save()
            print(f"booking instance of old_id {booking_instance.old_id}, pk {booking_instance.id} saved successfully")

    return Response({'message': 'Loading all Payment for Tour Booking successfully.'}, status=200)











