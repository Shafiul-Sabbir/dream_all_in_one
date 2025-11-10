from authentication.models import User, Country, Company
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from support.models import LoggedUser


@api_view(['POST'])
def load_LoggedUser(request, company_id):
    if company_id == 1:
        file_path = 'all_json/support/it/support_LoggedUser_it.json'
    elif company_id == 2:
        file_path = 'all_json/support/uk/support_LoggedUser_uk.json'
    elif company_id == 3:
        file_path = 'all_json/support/ziarah/support_LoggedUser_ziarah.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_user_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for user_data in all_user_data:
            fields = user_data.get('fields')
            print("raw User:", fields)
            print('\n')

            fields['old_id'] = user_data.get('pk')
            fields['company'] = company_instance

            user_id = fields.get('user')
            if user_id:
                user_instance = User.objects.filter(old_id = user_id, company = company_instance).first()
                fields['user'] = user_instance


            print("reformed User:", fields)
            print("-----")
            print("\n")
            
            if not LoggedUser.objects.filter(old_id=fields['old_id'], company = company_instance).exists():
                logged_user_obj = LoggedUser.objects.create(**fields)

                print(f"Saved logged User, id = {logged_user_obj.id}, old_id = {logged_user_obj.old_id}")
            else:
                print(f"Logged User with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all Logged Users successful.'}, status=200)