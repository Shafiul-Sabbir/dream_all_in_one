import os
from random import randrange
from time import process_time_ns
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
from authentication.models import Company
from cms.models import CMSMenu, CMSMenuContent,CMSMenuContentImage, CMSMenuContentImage
from cms.serializers import CMSMenuContentImageSerializer, CMSMenuContentImageListSerializer, CMSMenuContentImageMinimalSerializer,CMSMenuContentListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=CMSMenuContentImageSerializer,
    responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentImage(request):
    company_id = request.query_params.get('company_id')
    content_images = CMSMenuContentImage.objects.filter(company=company_id).all()
    print('content_images: ', content_images)

    total_elements = content_images.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    content_images = pagination.paginate_data(content_images)

    serializer = CMSMenuContentImageListSerializer(content_images, many=True)

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
    request=CMSMenuContentImageSerializer,
    responses=CMSMenuContentImageListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllContentImageWP(request):
    company_id = request.query_params.get('company_id')
    content_images = CMSMenuContentImage.objects.filter(company=company_id).all()
    print('content_images: ', content_images)

    serializer = CMSMenuContentImageMinimalSerializer(content_images, many=True)

    response = {
        'content_images': serializer.data,
    }

    return Response(response, status=status.HTTP_200_OK)





@extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getAllContentImageByMenuId(request, menu_id):
    content_images = CMSMenuContentImage.objects.filter(cms_menu=menu_id)
    total_elements = len(content_images)
    serializer = CMSMenuContentImageListSerializer(content_images, many=True)

    if content_images.count() > 0:
        response = {
            'total_elements' : total_elements,
            'content_images': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"CMSMenuContentImage with menu {menu_id} does't exist"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getAllContentImageListByMenuId(request, menu_id):
    try:
        # Filter all CMSMenuContentImage by menu_id
        images_qs = CMSMenuContentImage.objects.filter(cms_menu_id=menu_id)

        if not images_qs.exists():
            return Response(
                {'detail': "No content found."},
                status=status.HTTP_204_NO_CONTENT
            )

        # Prepare dictionary: { head: [images...] }
        content_images = {}

        for image in images_qs:
            # যদি cloudflare_image থাকে তাহলে ওটাই নাও, না থাকলে image.url
            image_url = image.cloudflare_image or (image.image.url if image.image else None)

            if not image_url:
                continue

            if image.head not in content_images:
                content_images[image.head] = []
            content_images[image.head].append(image_url)

        return Response(
            {'content_images': content_images},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def getACMSMenuContentImageByContentTitle(request, image_name):
    try:
        company_id = request.query_params.get('company_id')
        content_image = CMSMenuContentImage.objects.filter(head=image_name, company=company_id).first()
        serializer = CMSMenuContentImageSerializer(content_image)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContentImage with image_name '{image_name}' does not exist"}, 
                        status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCMSMenuContentImage(request):
    data = request.data
    print('data: ', data)
    print('content_type: ', request.content_type)

    filtered_data = {}

    for key, value in data.items():
        if value != '' and value != 0 and value != '0':
            filtered_data[key] = value
    print('\n')
    print('filtered_data: ', filtered_data)
    print('\n')

    company_id = data.get('company')
    menu_id = data.get('cms_menu')
    head = data.get('head')
    
    try:
        cms_menu_obj = CMSMenu.objects.get(pk=menu_id)
    except CMSMenu.DoesNotExist:
        return Response({'detail': "CMSMenu id {menu_id} doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return Response({'detail': "Company id {company_id} doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)

    for i in range(len(filtered_data) - 2):
        try:
            image = filtered_data[f'images[0][{i}]']
            print('image: ', image)
            print('image type: ', type(image))
            print('\n')
            filtered_data['image'] = image
            serializer = CMSMenuContentImageSerializer(data=filtered_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # CMSMenuContentImage.objects.create(cms_menu=cms_menu_obj, head=head, image=image)
        except KeyError:
            pass
    content_images = CMSMenuContentImage.objects.filter(cms_menu=cms_menu_obj, company=company).all()
    serializer = CMSMenuContentImageListSerializer(content_images, many=True)
    if content_images.count() > 0:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCMSMenuContentImage(request, pk):
    data = request.data
    print('data :', data)
    filtered_data = {}

    try:
        menu_obj = CMSMenuContentImage.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"Product id - {pk} doesn't exists"})

    for key, value in data.items():
        if value != '' and value != '0':
            filtered_data[key] = value

    print('filtered_data: ', filtered_data)

    image = filtered_data.get('image', None)

    if image is not None and type(image) == str:
        popped_image = filtered_data.pop('image')

    serializer = CMSMenuContentImageSerializer(menu_obj, data=filtered_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCMSMenuContentImage(request, pk):
    try:
        content_images = CMSMenuContentImage.objects.get(pk=pk)
        content_images.delete()
        return Response({'detail': f'CMSMenuContentImage id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContentImage id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


# @extend_schema(request=CMSMenuContentImageSerializer, responses=CMSMenuContentImageSerializer)
@api_view(['GET'])
def getContentImageListByMenuName(request, menu_name):
    try:
        company_id = request.query_params.get('company_id')
        matching_menus = CMSMenu.objects.filter(name__icontains=menu_name, company=company_id).all()
        print("company_id : ", company_id)
        print("matching menus : ", matching_menus)
        
        if matching_menus.exists():
            content_images_dict = {}
            for cms_menu in matching_menus:
                content_images = CMSMenuContentImage.objects.filter(cms_menu=cms_menu)
                
                for image in content_images:
                    menu_item_name = image.head
                    if image.cloudflare_image:
                        image_url = image.cloudflare_image
                    else:
                        image_url = image.image
                    
                    if menu_item_name in content_images_dict:
                        content_images_dict[menu_item_name].append(image_url)
                    else:
                        content_images_dict[menu_item_name] = [image_url]
            
            
            return Response({'content_images': content_images_dict}, status=status.HTTP_200_OK)
        else:
            
            return Response({'detail': f"No menus found matching '{menu_name}'"}, status=status.HTTP_404_NOT_FOUND)
    
    except ObjectDoesNotExist:
        
        return Response({'detail': f"No content images found for menu '{menu_name}'"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getContentAndImagesByMenuId(request, menu_id):
    try:
        company_id = request.query_params.get('company_id')
        cms_content_obj = CMSMenuContent.objects.filter(cms_menu=menu_id, company=company_id).all()
        # print("cms_content_obj : ", cms_content_obj)

        serializer = CMSMenuContentListSerializer(cms_content_obj, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CMSMenuContent.DoesNotExist:
        return Response({'detail': f"No content found for menu_id={menu_id}"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)