from django.conf import settings
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from django_currentuser.middleware import get_current_authenticated_user
from authentication.serializers import AdminUserMinimalListSerializer
from utils.utils import upload_to_cloudflare
from cms.models import *

class SerializerForCMSMenuParent(serializers.ModelSerializer):
    class Meta:
        model = CMSMenu
        fields = ['id', 'name',]

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
    cms_menu = CMSMenuListSerializer()
    class Meta:
        model = CMSMenuContent
        fields = ('id', 'cms_menu', 'name', 'order','value',)


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
        print("user in update cms menu content serializer: ", user)
        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=['updated_by'])
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
        user = get_current_authenticated_user()

        # Handle Cloudflare uploads only for fields that are present
        if 'image' in validated_data and validated_data['image']:
            print('\n')
            print("image found in validated data at create method, so going to upload.")
            validated_data['cloudflare_image'] = upload_to_cloudflare(validated_data['image'])

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
                validated_data['cloudflare_image'] = upload_to_cloudflare(validated_data['image'])
            else:
                print('\n')
                print("no new image provided or same image, so keeping the old one.")
                validated_data.pop('image', None)  # keep old image untouched

        modelObject = super().update(instance=instance, validated_data=validated_data)

        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=['updated_by'])

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


# BlogCategory serializer
class BlogCategoryListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BlogCategory
        fields = '__all__'




class BlogCategoryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ('id', 'name',)


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
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

# BlogCategory serializer
class BlogCountryListSerializer(serializers.ModelSerializer):
    
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Country
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


#Blog
class BlogListSerializer(serializers.ModelSerializer):
    blog_category = BlogCategoryListSerializer()
    blog_country = BlogCountryListSerializer()
    image = serializers.CharField(write_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Blog
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



class BlogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data):
        user = get_current_authenticated_user()

        # Handle Cloudflare uploads only for fields that are present
        if 'image' in validated_data and validated_data['image']:
            print('\n')
            print("image found in validated data at create method, so going to upload.")
            validated_data['cloudflare_image'] = upload_to_cloudflare(validated_data['image'])

        if 'meta_image' in validated_data and validated_data['meta_image']:
            print('\n')
            print("meta_image found in validated data at create method, so going to upload.")
            validated_data['meta_image_cloudflare'] = upload_to_cloudflare(validated_data['meta_image'])

        if 'fb_meta_image' in validated_data and validated_data['fb_meta_image']:
            print('\n')
            print("fb_meta_image found in validated data at create method, so going to upload.")
            validated_data['fb_meta_image_cloudflare'] = upload_to_cloudflare(validated_data['fb_meta_image'])

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
                validated_data['cloudflare_image'] = upload_to_cloudflare(validated_data['image'])
            else:
                print('\n')
                print("no new image provided or same image, so keeping the old one.")
                validated_data.pop('image', None)  # keep old image untouched

        # ✅ Meta image update
        if 'meta_image' in validated_data:
            print('\n')
            print("meta_image found in validated data at update method, so going to upload.")
            if validated_data['meta_image'] and validated_data['meta_image'] != instance.meta_image:
                validated_data['meta_image_cloudflare'] = upload_to_cloudflare(validated_data['meta_image'])
            else:
                print('\n')
                print("no new meta_image provided or same image, so keeping the old one.")
                validated_data.pop('meta_image', None)

        # ✅ Facebook meta image update
        if 'fb_meta_image' in validated_data:
            print('\n')
            print("fb_meta_image found in validated data at update method, so going to upload.")
            if validated_data['fb_meta_image'] and validated_data['fb_meta_image'] != instance.fb_meta_image:
                validated_data['fb_meta_image_cloudflare'] = upload_to_cloudflare(validated_data['fb_meta_image'])
            else:
                print('\n')
                print("no new fb_meta_image provided or same image, so keeping the old one.")
                validated_data.pop('fb_meta_image', None)

        modelObject = super().update(instance=instance, validated_data=validated_data)

        if user is not None:
            modelObject.updated_by = user
            modelObject.save(update_fields=['updated_by'])

        return modelObject

class BlogMinimaListSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Blog
        fields = '__all__'

#Blog Comments
class BlogCommentsListSerializer(serializers.ModelSerializer):

    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = BlogComments
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



class BlogCommentsMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComments
        fields = '__all__'


class BlogCommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BlogComments
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

#Review serializer
class ReviewListSerializer(serializers.ModelSerializer):
    # cms_content = CMSMenuContentMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Review
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



class ReviewMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
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

# MetaData serializer
class MetaDataListSerializer(serializers.ModelSerializer):
    cms_content = CMSMenuContentMinimalSerializer()
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = MetaData
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


class MetaDataMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaData
        fields = ('id', 'title', 'description',)

class MetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaData
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
    
# Tag serializer
class TagListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)
    updated_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Tag
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


class TagMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
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
    
