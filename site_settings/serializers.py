
from django.utils import translation
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from django_currentuser.middleware import get_current_authenticated_user
from utils.utils import upload_to_cloudflare
from site_settings.models import *




class MenuItemListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = MenuItem
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by




class MenuItemNestedSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'parent', 'menu_id', 'title', 'translate', 'type', 'icon', 'url', 'exact', 'children']




class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        # exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject




class RoleMenuListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = RoleMenu
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_role(self, obj):
        return obj.role.name if obj.role else obj.role

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by




class RoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleMenu
        fields = '__all__'
        # exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject




class GeneralSettingListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = GeneralSetting
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by

class GeneralSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSetting
        fields = '__all__'
        # exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']
    #     try:
    #         if self.favicon:
    #             self.cloudflare_favicon = self.upload_to_cloudflare(self.favicon)
    #             print(self.favicon, "self.favicon, ",self.cloudflare_favicon)
    #         if self.logo:
    #             self.cloudflare_logo = self.upload_to_cloudflare(self.logo)
    #         if self.footer_logo:
    #             self.cloudflare_footer = self.upload_to_cloudflare(self.footer_logo)
    #         if self.slider:
    #             self.cloudflare_slider = self.upload_to_cloudflare(self.slider)
    #     except Exception as e:
    #         print(f"Error uploading image to Cloudflare: {str(e)}")
    def create(self, validated_data):
        user = get_current_authenticated_user()

        # Handle Cloudflare uploads only for fields that are present
        if 'favicon' in validated_data and validated_data['favicon']:
            print('\n')
            print("favicon found in validated data at create method, so going to upload.")
            validated_data['cloudflare_favicon'] = upload_to_cloudflare(validated_data['favicon'])
        
        if 'logo' in validated_data and validated_data['favicon']:
            print('\n')
            print("logo found in validated data at create method, so going to upload.")
            validated_data['cloudflare_logo'] = upload_to_cloudflare(validated_data['logo'])
        
        if 'footer_logo' in validated_data and validated_data['footer_logo']:
            print('\n')
            print("footer_logo found in validated data at create method, so going to upload.")
            validated_data['cloudflare_footer'] = upload_to_cloudflare(validated_data['footer_logo'])
        
        if 'slider' in validated_data and validated_data['slider']:
            print('\n')
            print("slider found in validated data at create method, so going to upload.")
            validated_data['cloudflare_slider'] = upload_to_cloudflare(validated_data['slider'])
                   
        modelObject = super().create(validated_data=validated_data)

        if user is not None:
            modelObject.created_by = user
            modelObject.save(update_fields=['created_by'])

        return modelObject
      
    def update(self, instance, validated_data):
        user = get_current_authenticated_user()

        # ✅ Image field update: only upload if new image provided
        if 'favicon' in validated_data:
            print('\n')
            print("favicon found in validated data at update method, so going to upload.")
            if validated_data['favicon'] and validated_data['favicon'] != instance.favicon:
                validated_data['cloudflare_favicon'] = upload_to_cloudflare(validated_data['favicon'])
            else:
                print('\n')
                print("no new favicon provided or same favicon, so keeping the old one.")
                validated_data.pop('favicon', None)  # keep old image untouched
        
        if 'logo' in validated_data:
            print('\n')
            print("logo found in validated data at update method, so going to upload.")
            if validated_data['logo'] and validated_data['logo'] != instance.logo:
                validated_data['cloudflare_logo'] = upload_to_cloudflare(validated_data['logo'])
            else:
                print('\n')
                print("no new logo provided or same logo, so keeping the old one.")
                validated_data.pop('logo', None)  # keep old image untouched

        if 'footer_logo' in validated_data:
            print('\n')
            print("footer_logo found in validated data at update method, so going to upload.")
            if validated_data['footer_logo'] and validated_data['footer_logo'] != instance.footer_logo:
                validated_data['cloudflare_footer'] = upload_to_cloudflare(validated_data['footer_logo'])
            else:
                print('\n')
                print("no new footer_logo provided or same footer_logo, so keeping the old one.")
                validated_data.pop('footer_logo', None)  # keep old image untouched

        if 'slider' in validated_data:
            print('\n')
            print("slider found in validated data at update method, so going to upload.")
            if validated_data['slider'] and validated_data['slider'] != instance.slider:
                validated_data['cloudflare_slider'] = upload_to_cloudflare(validated_data['slider'])
            else:
                print('\n')
                print("no new slider provided or same slider, so keeping the old one.")
                validated_data.pop('slider', None)  # keep old image untouched
        
        modelObject = super().update(instance=instance, validated_data=validated_data)

        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=['updated_by'])

        return modelObject
    
class HomePageSliderListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = HomePageSlider
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by




class HomePageSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePageSlider
        fields = '__all__'
        # exclude = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def create(self, validated_data):
        user = get_current_authenticated_user()

        # Handle Cloudflare uploads only for fields that are present
        if 'image' in validated_data and validated_data['image']:
            print('\n')
            print("image found in validated data at create method, so going to upload.")
            validated_data['cloudflare_image_url'] = upload_to_cloudflare(validated_data['image'])

            modelObject = super().create(validated_data=validated_data)

        if user is not None:
            modelObject.created_by = user
            modelObject.save(update_fields=['created_by'])

        return modelObject
    
    def update(self, instance, validated_data):
        user = get_current_authenticated_user()

        # ✅ Image field update: only upload if new image provided
        if 'image' in validated_data:
            print('\n')
            print("image found in validated data at update method, so going to upload.")
            if validated_data['image'] and validated_data['image'] != instance.image:
                validated_data['cloudflare_image_url'] = upload_to_cloudflare(validated_data['image'])
            else:
                print('\n')
                print("no new image provided or same image, so keeping the old one.")
                validated_data.pop('image', None)  # keep old image untouched
        
        modelObject = super().update(instance=instance, validated_data=validated_data)

        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=['updated_by'])

        return modelObject


class ContactListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Contact
        fields = '__all__'
        extra_kwargs = {
            'created_at':{
                'read_only': True,
            },
            'updated_at':{
                'read_only': True,
            },
            'created_by':{
                'read_only': True,
            },
            'updated_by':{
                'read_only': True,
            },
        }

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else obj.created_by
        
    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else obj.updated_by




class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

    def create(self, validated_data):
        modelObject = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.created_by = user
        modelObject.save()
        return modelObject
    
    def update(self, instance, validated_data):
        modelObject = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user is not None:
            modelObject.updated_by = user
        modelObject.save()
        return modelObject



