import os
from PIL import Image

from random import randrange
import re
from urllib import response
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from authentication.serializers import AdminUserMinimalListSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from cms.models import CMSMenu, CMSMenuContentImage
from tour.models import Tour, TourContentImage
from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime

from tour.serializers.tour_content_serializers import TourContentImageListSerializer, TourContentImageSerializer, TourListSerializer
from utils.image_processing import parse_image_from_item, pil_image_to_uploaded_file
from utils.utils import reformed_head_or_name




# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=TourContentImageSerializer,
    responses=TourContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllTourContentImage(request):
    content_images = TourContentImage.objects.all()
    print('content_images: ', content_images)

    total_elements = content_images.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    content_images = pagination.paginate_data(content_images)

    serializer = TourContentImageListSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    return Response(response, status=status.HTTP_200_OK)




@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=TourContentImageSerializer,
    responses=TourContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllContentImageWP(request):
    content_images = TourContentImage.objects.all()
    print('content_images: ', content_images)

    serializer = TourContentImageListSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)





@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAllContentImageByTourId(request, tour_id):
    content_images = TourContentImage.objects.filter(tour=tour_id)
    serializer = TourContentImageListSerializer(content_images, many=True)

    if content_images.count() > 0:
        response = {
            'content_images': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"TourContentImage with Tour ID {tour_id} does't exist"}, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import Case, When, Value, CharField
from django.db.models.functions import Coalesce
from django.db.models import F

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=TourContentImageSerializer,
    responses=TourContentImageListSerializer
)

@api_view(['GET'])
def getAllContentImageListByTourId(request, tour_id):
    try:
        tour_obj = Tour.objects.get(pk=tour_id)
    except Tour.DoesNotExist:
        return Response({'detail': f"Tour id {tour_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    tour_content_images = TourContentImage.objects.filter(tour=tour_obj)

    if not tour_content_images.exists():
        return Response({'detail': "No tour Image found."}, status=status.HTTP_204_NO_CONTENT)

    # Serialize
    serializer = TourContentImageListSerializer(tour_content_images, many=True)
    print('serializer.data from getAllContentImageListByTourId : ', serializer.data)
    # Group by head (যদি তুমি head অনুযায়ী images group করতে চাও)
    # grouped_data = {}
    # for item in serializer.data:
    #     head = item.get("head")
    #     image_url = item.get("cloudflare_image") or item.get("image")
    #     if head not in grouped_data:
    #         grouped_data[head] = []
    #     grouped_data[head].append(image_url)
    tour_content_images_list = []
    for item in serializer.data:
        image_url = item.get("cloudflare_image_url") or item.get("image")
        tour_content_images_list.append({
            "id": item.get("id"),
            "image": image_url
        })


    response = {
        "tour_id": tour_obj.id,
        "tour_name": tour_obj.name,
        # "content_images": grouped_data
        "tour_content_images_list": tour_content_images_list
    }

    return Response(response, status=status.HTTP_200_OK)

@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getATourContentImageByImageHead(request, image_head):
    try:
      
        content_images = TourContentImage.objects.filter(head=image_head)
        
      
        serializer = TourContentImageSerializer(content_images, many=True)
        
       
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        
        return Response({'detail': f"TourContentImage with head '{image_head}' does not exist"}, 
                        status=status.HTTP_404_NOT_FOUND)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_CREATE.name])
def createTourContentImage(request):
    print("Creating a new tourContentImage...")

    # make mutable copy
    data = request.data.copy()
    print("Requested form-data:", data)

    # convert to normal dict
    processed_data = dict(data)
    # print("Processed form-data:", processed_data)

    # single value fields (unwrap list → str)
    for key, value in processed_data.items():
        if isinstance(value, list) :
            processed_data[key] = value[0]
    print("Processed form-data:", processed_data)

    # Tour validation
    tour_id = processed_data.get('tour_id')
    head = processed_data.get('head')

    try:
        tour_obj = Tour.objects.get(pk=tour_id)
    except Tour.DoesNotExist:
        return Response({'detail': f"Tour id {tour_id} doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

    # Only pick image keys
    image_keys = [key for key in processed_data.keys() if key.startswith("images[0]")]
    errors, created = [], []
    print('image_keys: ', image_keys)
    for key in image_keys:
        image = processed_data.get(key)
        print(f"Processing {key} => {image}")
        serializer = TourContentImageSerializer(data={
            'tour': tour_obj.id,
            'head': head,
            'image': image
        })
        if serializer.is_valid():
            serializer.save()
            created.append(serializer.data)
        else:
            errors.append({key: serializer.errors})

    tour_content_images = TourContentImage.objects.filter(tour=tour_obj)
    serializer = TourContentImageListSerializer(tour_content_images, many=True)
    # serializer = TourContentImageListSerializer(tour_content_images,context={'request': request}, many=True)

    response = {
        'tour_id': tour_obj.id,
        'tour_name': tour_obj.name,
        'content_images': serializer.data,
        'errors': errors
    }
    status_code = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
    return Response(response, status=status_code)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_UPDATE.name])
# @parser_classes([MultiPartParser, FormParser])
@api_view(['PUT'])
def updateTourContentImage(request, pk):
    print('updateTourContentImage called with pk:', pk)
    # make mutable copy
    data = request.data.copy()
    print("Requested form-data:", data)
    print('\n')

    # convert to normal dict
    processed_data = dict(data)
    # print("Processed form-data:", processed_data)

    validated_data = {}

    # single value fields (unwrap list → str)
    for key, value in processed_data.items():
        if isinstance(value, list) and not key.startswith("images[0]"):
            validated_data[key] = value[0]
    print("validated form-data:", validated_data)
    print('\n')



    try:
        content_image = TourContentImage.objects.get(pk=pk)
        print('content_image: ', content_image)
        print('content_image.image: ', content_image.image)
    except TourContentImage.DoesNotExist:
        return Response({'detail': f"TourContentImage with id {pk} not found."},
                        status=status.HTTP_404_NOT_FOUND)

    
    print('\n')


    # update using serializer
    # file fields (image etc.)
    print("request files:", request.FILES)
    if "images[0][0]" in request.FILES:
        validated_data["update_image"] = True
        validated_data["image"] = request.FILES["images[0][0]"]
    print("validated form-data for update:", validated_data)

    serializer = TourContentImageSerializer(instance=content_image, data=validated_data, partial=True)

    if serializer.is_valid():
        serializer.save()

        updated_content = serializer.data
        print('updated_content: ', updated_content)
        print('updated_content.image: ', updated_content.get('image'))
        print('\n')

        # update হওয়ার পর নতুন পুরো list পাঠানো হবে
        tour_content_images = TourContentImage.objects.filter(tour=content_image.tour)
        list_serializer = TourContentImageListSerializer(tour_content_images, many=True)

        response = {
            'tour_id': content_image.tour.id,
            'tour_name': content_image.tour.name,
            'updated_content': serializer.data,
            'all_content_images': list_serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # return Response({"message": "Update functionality is not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DELETE.name])
def deleteTourContentImage(request, pk):
    try:
        content_image = TourContentImage.objects.get(pk=pk)
        content_image.delete()
        return Response({'detail': f'TourContentImage id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"TourContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=TourContentImageSerializer, responses=TourContentImageSerializer)
@api_view(['GET'])
def getContentImageListByTourName(request, tour_name):
    try:
        
        matching_tours = Tour.objects.filter(name__icontains=tour_name)
        
        if matching_tours.exists():
            
            content_images_dict = {}
            
            
            for tour in matching_tours:
                
                content_images = TourContentImage.objects.filter(tour=tour)
                
                
                for image in content_images:
                    tour_content_image_head = image.head
                    if image.cloudflare_image_url:
                        image_url = image.cloudflare_image_url
                    else:
                        image_url = image.image
                    
                    if tour_content_image_head in content_images_dict:
                        content_images_dict[tour_content_image_head].append(image_url)
                    else:
                        content_images_dict[tour_content_image_head] = [image_url]
            
            
            return Response({'content_images': content_images_dict}, status=status.HTTP_200_OK)
        else:
            
            return Response({'detail': f"No Tour found matching '{tour_name}'"}, status=status.HTTP_404_NOT_FOUND)
    
    except ObjectDoesNotExist:
        
        return Response({'detail': f"No Tour content images found for Tour '{tour_name}'"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getContentAndImagesByTourId(request, tour_id):
    try:
        tour_obj = Tour.objects.filter(id=tour_id)

        serializer = TourListSerializer(tour_obj, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Tour.DoesNotExist:
        return Response({'detail': f"No content found for tour_id={tour_id}"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def populateToursWithMenuContentImages(request):
    cms_menu_id = 11
    try:
        cms_menu = CMSMenu.objects.get(id=cms_menu_id)
    except CMSMenu.DoesNotExist:
        return Response({'detail': f"No content found for cms_menu_id={cms_menu_id}"}, status=status.HTTP_404_NOT_FOUND)
    
    # Query once
    cms_menu_content_images = CMSMenuContentImage.objects.filter(cms_menu=cms_menu)
    tours = Tour.objects.all()
    total_tour = tours.count()
    total_cms_images = cms_menu_content_images.count()

    # Step 1: Tour dict → {reformed_name: tour_obj}
    tour_dict = {
        reformed_head_or_name(tour.name): tour
        for tour in tours
    }

    # Step 2: Image dict → {reformed_head: [image_obj, ...]}
    image_dict = {}
    for img in cms_menu_content_images:
        key = reformed_head_or_name(img.head)
        image_dict.setdefault(key, []).append(img)

    # Step 3: Match tours ↔ images by reformed key
    cms_images_list = []
    for key, tour in tour_dict.items():
        if key in image_dict:
            for img in image_dict[key]:
                cms_images_list.append({
                    'tour_id': tour.id,
                    'reformed_tour_name': key,
                    'CMS_content_image_id': img.id,
                    'reformed_CMS_image_head': key,
                    'image': img.image.path,
                    'cloudflare_image_url': img.cloudflare_image,
                })


    # step 4: populate TourContentImage table by CMSMenuContentImage table's matchng data.
    tour_content_image_creation_count = 0
    for item in cms_images_list:
        tour_id = item['tour_id']
        print("tour_id : ", tour_id)
        try:
            tour = Tour.objects.get(id = tour_id)
        except Tour.DoesNotExist:
            return Response({"error" : f"tour doesnot exists with tour_id {tour_id}"})
        
        all_images = TourContentImage.objects.filter(tour=tour)
        all_images_url_list = [single_image.cloudflare_image_url for single_image in all_images]
        
        image_url = item['cloudflare_image_url']
        image_path = item['image']
        image_obj = parse_image_from_item(image_path)
        image = image_obj['image']
        image_name = image_obj['image_name']

        # checking if this image name is already exists for this tour or not

        if image_url not in all_images_url_list:

            # convert PIL image into InMemoryUploadedFile 
            uploaded_image = pil_image_to_uploaded_file(image, name=image_name)
            
            tour_content_image_data = {}
            tour_content_image_data['tour'] = tour
            tour_content_image_data['head'] = item['reformed_tour_name']
            tour_content_image_data['image'] = uploaded_image   # Now assigning original image file, not PIL
            tour_content_image_data['cloudflare_image_url'] = image_url

            print("tour_content_image_data : ", tour_content_image_data)
            
            tour_content_image = TourContentImage(**tour_content_image_data)

            # setting a temporary variable to bypass save() method inside the model
            tour_content_image._skip_cloudflare = True    

            tour_content_image.save()

            print("tour content image id : ", tour_content_image.id)

        else:
            print(f"Image '{image_name}' already exists for tour '{tour.name}', skipping...")
    
        
    return Response({
        "status": "OK",
        "total_tour" : total_tour,
        "total_cms_images_for_cms_menu_id_11" : total_cms_images,
        "total_cms_images_for_present_tours": len(cms_images_list),
        "cms_images_list": cms_images_list,
    }, status=status.HTTP_200_OK)
