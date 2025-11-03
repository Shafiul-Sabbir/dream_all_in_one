from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from tour.models import OldAgentBooking
from authentication.models import Company

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
        print('\n')
        print("booking_id : ", booking_data.get('pk'))
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

            print('\n')


        print("modified booking data : ", fields)

                    
    return Response({'message': 'Loading all Old Agent Bookings successful.'}, status=200)