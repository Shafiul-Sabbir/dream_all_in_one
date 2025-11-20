import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from cms.models import CMSMenuContent, CMSMenu
from cms.serializers import CMSMenuContentSerializer, CMSMenuContentListSerializer

from commons.pagination import Pagination
from commons.enums import PermissionEnum

import datetime


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=CMSMenuContentListSerializer,
    responses=CMSMenuContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])

def getAllCMSMenuContent(request):

    company_id = request.query_params.get('company_id')
    # menu_items = CMSMenuContent.objects.all() # response time 100ms for 43 queries

    menu_items = CMSMenuContent.objects.select_related('created_by', 'updated_by', 'cms_menu').prefetch_related(
        'cms_menu__cms_menu_content_images'  # reverse relation from CMSMenuContentImage
        ).filter(company=company_id)
    # response time 40ms for 14 queries

    # menu_items = CMSMenuContent.objects.select_related('created_by', 'updated_by', 'cms_menu')
    # response time 37 ms for 13 queries
    total_elements = menu_items.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    menu_items = pagination.paginate_data(menu_items)

    serializer = CMSMenuContentListSerializer(menu_items, many=True)

    response = {
        'total_elements': total_elements,
        'menu_items': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
    }
    return Response(response, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=CMSMenuContentListSerializer,
    responses=CMSMenuContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentWithoutPagination(request):
    company_id = request.query_params.get('company_id')

    # menu_items = CMSMenuContent.objects.all()
    menu_items = CMSMenuContent.objects.select_related('created_by', 'updated_by', 'cms_menu').prefetch_related(
        'cms_menu__cms_menu_content_images'  # reverse relation from CMSMenuContentImage
        ).filter(company=company_id)
    
    total_elements = menu_items.count()


    serializer = CMSMenuContentListSerializer(menu_items, many=True)

    response = {
        'total_elements': total_elements,
        'menu_items': serializer.data,
    }
    return Response(response, status=status.HTTP_200_OK)




@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=CMSMenuContentListSerializer,
    responses=CMSMenuContentListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
def getAllCMSMenuContentByCMSMenuId(request, menu_id):

    menu_contents = CMSMenuContent.objects.filter(cms_menu=menu_id).all()
    total_elements = len(menu_contents)
    if menu_contents:
        serializer = CMSMenuContentListSerializer(menu_contents, many=True)
        response = {
        'total_elements': total_elements,
        'menu_contents': serializer.data,
        }

        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': "No content found."}, status=status.HTTP_204_NO_CONTENT)



# @extend_schema(request=CMSMenuContentSerializer, responses=CMSMenuContentSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
def getACMSMenuContent(request,pk):
    
    try:
        menu_item = CMSMenuContent.objects.get(id=pk)
        print("menu_item : ", menu_item)
        serializer = CMSMenuContentListSerializer(instance=menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContent name - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCMSMenuContent(request):
    data = request.data
    print('data: ', data)
    
    serializer = CMSMenuContentSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCMSMenuContent(request, pk):
    data = request.data

    try:
        menu_item = CMSMenuContent.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContent id - {pk} doesn't exists"})

    serializer = CMSMenuContentSerializer(menu_item, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCMSMenuContent(request, pk):
    try:
        menu_item = CMSMenuContent.objects.get(pk=pk)
        menu_item.delete()
        return Response({'detail': f'CMSMenuContent id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=CMSMenuContentSerializer, responses=CMSMenuContentSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])

def getCMSMenuContentByCMSMenuID(request, pk):
    try:
        main_menu = CMSMenu.objects.get(id=pk) 
        # menu_contents = CMSMenuContent.objects.filter(cms_menu=main_menu) # response time 13ms for 2 queries
        # menu_contents = CMSMenuContent.objects.filter(cms_menu=main_menu).select_related('created_by', 'updated_by', 'cms_menu').prefetch_related(
        # 'cms_menu__cms_menu_content_images'  # reverse relation from CMSMenuContentImage
        # )
        """ 
        CMSMenuContentSerializer er moddhe 'get_cloudflare_image' method ta call kora nai, tai ai serializer tai 
        amara use korbo, 'get_cloudflare_image' method er moddhe CMSMenuContentImage k niye kaj kora ase, 
        tai amra amader query er vitor theke reverse relation er part tuku maane prefetch_related er part tuku 
        baad dite pari. ete amader query o akta kom lagtese, response time o kisu komtese. large dataset e 
        aitar optimization ta bujha jabe.  
         """
        
        menu_contents = CMSMenuContent.objects.filter(cms_menu=main_menu).select_related('created_by', 'updated_by', 'cms_menu')
        serializer = CMSMenuContentSerializer(menu_contents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenuContent id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_menu_content_by_slug(request,slug,menu_name='Home'):
    if request.query_params.get('menu_name') :
        menu_name = request.query_params.get('menu_name')
    else: 
        menu_name = 'Home'
    print("menu name : ", menu_name)
    company_id = request.query_params.get('company_id')
    try:
        menu = CMSMenu.objects.filter(name=menu_name, company=company_id).first()
        print("menu : ", menu)
        menu_content = CMSMenuContent.objects.filter(slug=slug, cms_menu=menu, company=company_id).first()

        if menu_content:
            serializer = CMSMenuContentListSerializer(instance=menu_content)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': f"CMSMenuContent with slug '{slug}' not found for menu '{menu_name}'"},
                            status=status.HTTP_404_NOT_FOUND)
    except ObjectDoesNotExist:
        return Response({'detail': f"CMSMenu with name '{menu_name}' does not exist"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(request=CMSMenuContentSerializer, responses=CMSMenuContentSerializer)
@api_view(['GET'])
def getCMSMenuContentByCMSMenuName(request, menu_name):
    company_id = request.query_params.get('company_id')

    try:
        main_menu = CMSMenu.objects.filter(name__icontains=menu_name, company=company_id).first()
        menu_contents = CMSMenuContent.objects.filter(cms_menu=main_menu)
        serializer = CMSMenuContentSerializer(menu_contents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except CMSMenu.DoesNotExist:
        return Response({'detail': f"CMSMenu with menu_name '{menu_name}' does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)