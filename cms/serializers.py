from django.conf import settings

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from django_currentuser.middleware import get_current_authenticated_user

from authentication.serializers import AdminUserMinimalListSerializer

from cms.models import *


class SerializerForCMSMenuParent(serializers.ModelSerializer):
    class Meta:
        model = CMSMenu
        fields = ['id', 'name']




class CMSMenuListSerializer(serializers.ModelSerializer):
    parent = SerializerForCMSMenuParent()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CMSMenu
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




class CMSMenuMinimalSerializer(serializers.ModelSerializer):
    parent = SerializerForCMSMenuParent()
    class Meta:
        model = CMSMenu
        fields = ['id', 'name', 'parent']




class CMSMenuNestedSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    class Meta:
        model = CMSMenu
        fields = ('id', 'name', 'parent', 'children', 'position')




class CMSMenuSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CMSMenu
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


class CMSMenuContentListSerializer(serializers.ModelSerializer):
    cms_menu = CMSMenuMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    cloudflare_image = serializers.SerializerMethodField()
    class Meta:
        model = CMSMenuContent
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

    
 
    def get_cloudflare_image(self, obj):
        image_instance = CMSMenuContentImage.objects.filter(head=obj.name,cms_menu=obj.cms_menu)
        images =[]
        for item in image_instance:
            images.append(item.cloudflare_image)
        return images

           
class CMSMenuContentMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSMenuContent
        fields = ('id', 'cms_menu', 'name', 'value','order')




class CMSMenuContentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CMSMenuContent
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




class CMSMenuContentImageListSerializer(serializers.ModelSerializer):
    cms_menu = CMSMenuMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CMSMenuContentImage
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



class CMSMenuContentImageMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSMenuContentImage
        fields = ('id', 'cms_menu', 'head', 'image')




class CMSMenuContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSMenuContentImage
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







#itinenary



class ItineraryListSerializer(serializers.ModelSerializer):
    cms_content = CMSMenuContentMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Itinerary
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



class ItineraryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ('id', 'title', 'description', 'location')




class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
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










#adding email


class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        fields = '__all__'


class SendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmail
        fields = '__all__'

