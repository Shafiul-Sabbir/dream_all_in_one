from authentication.models import User, Country
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from authentication.models import Company, User
from site_settings.models import GeneralSetting, HomePageSlider

@api_view(['POST'])
def load_GeneralSetting(request, company_id):
    if company_id == 1:
        file_path = 'all_json/site_settings/it/site_settings_GeneralSetting_it.json'
    elif company_id == 2:
        file_path = 'all_json/site_settings/uk/site_settings_GeneralSetting_uk.json'

    with open(file_path, 'r', encoding='utf-8') as file:
        all_setting_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for setting_data in all_setting_data:
            fields = setting_data.get('fields')
            print("raw Setting:", fields)
            print('\n')

            fields['old_id'] = setting_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None


            print("reformed Setting:", fields)
            print("-----")
            print("\n")
            
            if not GeneralSetting.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                setting_obj = GeneralSetting.objects.create(**fields)

                print(f"Saved Setting, id = {setting_obj.id}, old_id = {setting_obj.old_id}")
            else:
                print(f"Setting with old_id = {fields['old_id']} already exists. Skipping.")
    
    return Response({'message': 'Loading all Setting successful.'}, status=200)


@api_view(['POST'])
def load_HomePageSlider(request, company_id):
    if company_id == 1:
        file_path = 'all_json/site_settings/it/site_settings_HomePageSlider_it.json'
    elif company_id == 2:
        file_path = 'all_json/site_settings/uk/site_settings_HomePageSlider_uk.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        all_slider_data = json.load(file)
        company_instance = Company.objects.get(id=company_id)

        for slider_data in all_slider_data:
            fields = slider_data.get('fields')
            print("raw HomePageSlider:", fields)
            print('\n')

            fields['old_id'] = slider_data.get('pk')
            fields['company_id'] = company_instance

            # handle created_by and updated_by fields
            created_by_old_id = fields.get('created_by')
            updated_by_old_id = fields.get('updated_by')
            if created_by_old_id:
                try:
                    created_by_user = User.objects.get(old_id=created_by_old_id, company_id=company_instance)
                    fields['created_by'] = created_by_user
                except User.DoesNotExist:
                    fields['created_by'] = None
            else:
                fields['created_by'] = None

            if updated_by_old_id:
                try:
                    updated_by_user = User.objects.get(old_id=updated_by_old_id, company_id=company_instance)
                    fields['updated_by'] = updated_by_user
                except User.DoesNotExist:
                    fields['updated_by'] = None
            else:
                fields['updated_by'] = None


            print("reformed HomePageSlider:", fields)
            print("-----")
            print("\n")
            
            # Assuming HomePageSlider is a model similar to GeneralSetting
            if not HomePageSlider.objects.filter(old_id=fields['old_id'], company_id=company_instance).exists():
                slider_obj = HomePageSlider.objects.create(**fields)

                print(f"Saved HomePageSlider, id = {slider_obj.id}, old_id = {slider_obj.old_id}")
            else:
                print(f"HomePageSlider with old_id = {fields['old_id']} already exists. Skipping.")
    return Response({'message': 'Loading all HomePageSlider successful.'}, status=200)