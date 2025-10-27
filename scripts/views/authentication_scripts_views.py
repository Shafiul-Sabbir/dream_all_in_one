from authentication.models import User, Country
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from authentication.models import Permission, Company, Role


@api_view(['POST'])
def load_users(request, company_id):
    # Logic to load users for the given company_id
    # all_users = User.objects.all()
    # print("all users : ", all_users)
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_user_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_user_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_user_data = json.load(file)
        for user in all_user_data:
            fields = user.get('fields')
            fields['old_id'] = user.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance
            print("user:", fields)

            #we will assign the created_by and updated_by later
            role_id = fields.pop('role', None)
            if role_id:
                role_instance = Role.objects.filter(old_id=role_id, company_id=company_instance).first()
                fields['role'] = role_instance
            fields.pop('created_by', None)
            fields.pop('updated_by', None)
            if not User.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                user_obj = User.objects.create(**fields)

                print(f"Saved user, id = {user_obj.id}, old_id = {user_obj.old_id}")
            else:
                print(f"user with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all users successful.'}, status=200)

@api_view(['POST'])
def handle_user_metadata(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_user_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_user_uk.json'

    all_db_users = User.objects.filter(company_id=company_id)
    with open(file_path, 'r', encoding='utf-8') as file:
        all_user_data = json.load(file)
        user_data_dict = {user.get('pk'): user.get('fields') for user in all_user_data}

        for user in all_db_users:
            old_id = user.old_id
            if old_id in user_data_dict:
                fields = user_data_dict[old_id]
                created_by_old_id = fields.get('created_by')
                updated_by_old_id = fields.get('updated_by')
                created_at_old_id = fields.get('created_at')
                updated_at_old_id = fields.get('updated_at')

                if created_by_old_id:
                    created_by_user = User.objects.filter(old_id=created_by_old_id, company_id=company_id).first()
                    if created_by_user:
                        user.created_by = created_by_user

                if updated_by_old_id:
                    updated_by_user = User.objects.filter(old_id=updated_by_old_id, company_id=company_id).first()
                    if updated_by_user:
                        user.updated_by = updated_by_user

                if created_at_old_id:
                    user.created_at = created_at_old_id

                if updated_at_old_id:
                    user.updated_at = updated_at_old_id

                user.save()
                print(f"Updated metadata for user id = {user.id}, old_id = {user.old_id}")
            else:
                print(f"No data found for user with old_id = {old_id}. Skipping.")
    
    return Response({'message': 'Handled all users Meta data.'}, status=200)

@api_view(['POST'])
def load_roles(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_role_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_role_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_role_data = json.load(file)
        for role in all_role_data:
            fields = role.get('fields')
            fields['old_id'] = role.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance
            print("role:", fields)

            # Extract permission IDs and remove from fields, will assign later
            permission_ids = fields.pop('permissions', [])

            #we will assign the created_by and updated_by later
            fields.pop('created_by', None)
            fields.pop('updated_by', None)
            if not Role.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                role_obj = Role.objects.create(**fields)

                if permission_ids:
                    new_permission_ids = []
                    for id in permission_ids:
                        permission_instance = Permission.objects.filter(old_id=id, company_id=company_instance).first()
                        new_permission_ids.append(permission_instance.id)
                    print("new_permission_ids:", new_permission_ids)
                    role_obj.permissions.set(new_permission_ids)
                print(f"Saved permission, id = {role_obj.id}, old_id = {role_obj.old_id}")
            else:
                print(f"Role with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all roles successful.'}, status=200)

@api_view(['POST'])
def handle_role_metadata(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_role_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_role_uk.json'

    all_db_roles = Role.objects.filter(company_id=company_id)
    with open(file_path, 'r', encoding='utf-8') as file:
        all_role_data = json.load(file)
        role_data_dict = {role.get('pk'): role.get('fields') for role in all_role_data}

        for role in all_db_roles:
            old_id = role.old_id
            if old_id in role_data_dict:
                fields = role_data_dict[old_id]
                created_by_old_id = fields.get('created_by')
                updated_by_old_id = fields.get('updated_by')
                created_at_old_id = fields.get('created_at')
                updated_at_old_id = fields.get('updated_at')

                if created_by_old_id:
                    created_by_user = User.objects.filter(old_id=created_by_old_id, company_id=company_id).first()
                    if created_by_user:
                        role.created_by = created_by_user

                if updated_by_old_id:
                    updated_by_user = User.objects.filter(old_id=updated_by_old_id, company_id=company_id).first()
                    if updated_by_user:
                        role.updated_by = updated_by_user

                if created_at_old_id:
                    role.created_at = created_at_old_id

                if updated_at_old_id:
                    role.updated_at = updated_at_old_id

                role.save()
                print(f"Updated metadata for role id = {role.id}, old_id = {role.old_id}")
            else:
                print(f"No data found for role with old_id = {old_id}. Skipping.")
    
    return Response({'message': 'Handled all roles Meta data.'}, status=200)


@api_view(['POST'])
def load_permissions(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_permission_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_permission_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_permission_data = json.load(file)
        for permission in all_permission_data:
            fields = permission.get('fields')
            fields['old_id'] = permission.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance
            print("permission:", fields)
            fields.pop('created_by', None)
            fields.pop('updated_by', None)
            if not Permission.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                permission_obj = Permission.objects.create(**fields)
                print(f"Saved permission, id = {permission_obj.id}, old_id = {permission_obj.old_id}")
            else:
                print(f"Permission with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all permissions successful.'}, status=200)

@api_view(['POST'])
def handle_permission_metadata(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_permission_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_permission_uk.json'

    all_db_permissions = Permission.objects.filter(company_id=company_id)
    with open(file_path, 'r', encoding='utf-8') as file:
        all_permission_data = json.load(file)
        permission_data_dict = {permission.get('pk'): permission.get('fields') for permission in all_permission_data}

        for permission in all_db_permissions:
            old_id = permission.old_id
            if old_id in permission_data_dict:
                fields = permission_data_dict[old_id]
                created_by_old_id = fields.get('created_by')
                updated_by_old_id = fields.get('updated_by')
                created_at_old_id = fields.get('created_at')
                updated_at_old_id = fields.get('updated_at')

                if created_by_old_id:
                    created_by_user = User.objects.filter(old_id=created_by_old_id, company_id=company_id).first()
                    if created_by_user:
                        permission.created_by = created_by_user

                if updated_by_old_id:
                    updated_by_user = User.objects.filter(old_id=updated_by_old_id, company_id=company_id).first()
                    if updated_by_user:
                        permission.updated_by = updated_by_user

                if created_at_old_id:
                    permission.created_at = created_at_old_id

                if updated_at_old_id:
                    permission.updated_at = updated_at_old_id

                permission.save()
                print(f"Updated metadata for permission id = {permission.id}, old_id = {permission.old_id}")
            else:
                print(f"No data found for permission with old_id = {old_id}. Skipping.")
    
    return Response({'message': 'Handled all permissions Meta data.'}, status=200)

@api_view(['POST'])
def load_countries(request, company_id):
    # all_countries = Country.objects.all()
    # print("all countries : ", all_countries)

    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_country_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_country_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_country_data = json.load(file)
        print("all_country_data:", all_country_data)
        for country in all_country_data:
            fields = country.get('fields')
            fields['old_id'] = country.get('pk')
            company_instance = Company.objects.get(id=company_id)
            fields['company_id'] = company_instance
            print("country:", fields)
            #we will assign the created_by and updated_by later
            fields.pop('created_by', None)
            fields.pop('updated_by', None)
            print('\n')
            if not Country.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                country_obj = Country.objects.create(**fields)
                print(f"Saved country, id = {country_obj.id}, old_id = {country_obj.old_id}")
            else:
                print(f"Country with old_id = {fields['old_id']} already exists. Skipping.")
    return Response({'message': 'Loading all countries'}, status=200)

@api_view(['POST'])
def handle_country_metadata(request, company_id):
    if company_id == 1:
        file_path = 'all_json/authentication/it/authentication_country_it.json'
    elif company_id == 2:
        file_path = 'all_json/authentication/uk/authentication_country_uk.json'

    all_db_countries = Country.objects.filter(company_id=company_id)
    with open(file_path, 'r', encoding='utf-8') as file:
        all_country_data = json.load(file)
        country_data_dict = {country.get('pk'): country.get('fields') for country in all_country_data}

        for country in all_db_countries:
            old_id = country.old_id
            if old_id in country_data_dict:
                fields = country_data_dict[old_id]
                created_by_old_id = fields.get('created_by')
                updated_by_old_id = fields.get('updated_by')
                created_at_old_id = fields.get('created_at')
                updated_at_old_id = fields.get('updated_at')

                if created_by_old_id:
                    created_by_user = User.objects.filter(old_id=created_by_old_id, company_id=company_id).first()
                    if created_by_user:
                        country.created_by = created_by_user

                if updated_by_old_id:
                    updated_by_user = User.objects.filter(old_id=updated_by_old_id, company_id=company_id).first()
                    if updated_by_user:
                        country.updated_by = updated_by_user

                if created_at_old_id:
                    country.created_at = created_at_old_id

                if updated_at_old_id:
                    country.updated_at = updated_at_old_id

                country.save()
                print(f"Updated metadata for country id = {country.id}, old_id = {country.old_id}")
            else:
                print(f"No data found for country with old_id = {old_id}. Skipping.")
    
    return Response({'message': 'Handled all countries Meta data.'}, status=200)