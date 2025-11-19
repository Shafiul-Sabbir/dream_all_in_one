from urllib import request
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions

from cms.models import Blog, CMSMenu,Blog,Blog
from cms.serializers import BlogSerializer, BlogListSerializer,BlogMinimaListSerializer
from cms.filters import *
from commons.pagination import Pagination
from commons.enums import PermissionEnum
import os
import datetime
import requests


# Create your views here.

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
        OpenApiParameter("things_to_do", required=False),
        OpenApiParameter("country", required=False),

  ],
    request=BlogListSerializer,
    responses=BlogListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])

def getAllBlog(request):
    company_id = request.query_params.get('company_id')
    page = request.query_params.get('page')
    size = request.query_params.get('size')
    things_to_do = request.query_params.get('things_to_do', None)
    country = request.query_params.get('country', None)
    
    # handle country filtering using country id
    if country is not None:
        # Filter blogs by country if provided
        # print('country: ', country)
        # blogs = Blog.objects.filter(blog_country = country)
        blogs = Blog.objects.filter(blog_country=country, company=company_id).select_related('cms_content', 'blog_category', 'blog_country', 'created_by', 'updated_by')
        # print('blogs from country handling: ', blogs)
    else:
        # Get all blogs if no country filter is provided
        # blogs = Blog.objects.all()
        blogs = Blog.objects.filter(company=company_id).select_related('cms_content', 'blog_category', 'blog_country', 'created_by', 'updated_by')
    
    # handle things_to_do filter
    if things_to_do == 'true':
        # Filter blogs that are marked as things to do in the title
        blogs = blogs.filter(title__icontains = "things to do")  # Adjust the filter condition as needed
    elif things_to_do == 'false':
        # Filter blogs that are not marked as things to do in the title
        blogs = blogs.filter(~Q(title__icontains = "things to do"))  # Adjust the filter condition as needed
    else:
        # If things_to_do is not specified, return all blogs
        blogs = blogs.all()
            
    total_elements = blogs.count()

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    blogs = pagination.paginate_data(blogs)

    serializer = BlogListSerializer(blogs, many=True)

    response = {
        'blogs': serializer.data,
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
    request=BlogListSerializer,
    responses=BlogListSerializer
)
@api_view(['GET'])
def getAllBlogWithoutPagination(request):
    company_id = request.query_params.get('company_id')
    blogs = Blog.objects.filter(company=company_id).all()
    total_elements = blogs.count()

    serializer = BlogListSerializer(blogs, many=True)

    response = {
        'blogs': serializer.data,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)





@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
  ],
    request=BlogListSerializer,
    responses=BlogListSerializer
)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])
# def getAllBlogByCMSMenuId(request, menu_id):
# 	blogs = Blog.objects.filter(cms_content=menu_id)

# 	serializer = BlogListSerializer(blogs,many=True)
# 	return Response(serializer.data, status=status.HTTP_200_OK)

# 	with connection.cursor() as cursor:
# 		cursor.execute('''
# 						SELECT
# 							cms_menu_id AS cms_menu,
# 							jsonb_build_object(
# 				             	'title', MAX(title),
#                     			'description', MAX(description),
#                     			'location', MAX(location)
# 				            ) AS data
# 						FROM cms_Blog WHERE cms_menu_id=%s
# 						GROUP BY cms_menu_id
# 						ORDER BY cms_menu_id;
# 						''', [menu_id])
  
# 		row = cursor.fetchall()
        
# 	if rows:
# 			my_data = [{'title': row[0],'description':row[1] } for row in rows]
            
# 			response = {'menu_contents': my_data}
# 			return JsonResponse(response, status=status.HTTP_200_OK)
        
# 	else:
# 		return JsonResponse({'detail': "No content found."}, status=status.HTTP_204_NO_CONTENT)
        
        






@extend_schema(request=BlogSerializer, responses=BlogSerializer)
@api_view(['GET'])
def getBlog(request, pk):
    try:
        menu_item = Blog.objects.get(pk=pk)
        serializer = BlogSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Blog id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createBlog(request):
    data = request.data
    print('data: ', data)
    
    serializer = BlogSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateBlog(request, pk):
    data = request.data
    print('data:', data)
    
    try:
        blog_instance = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({'detail': f"Blog id - {pk} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

   
    filtered_data = {}
    restricted_values = ['', ' ', '0', 'undefined', None]
    
    for key, value in data.items():
        if key == "file" and isinstance(value, str):
            continue  
        
        if value not in restricted_values:
            filtered_data[key] = value
        else:
            filtered_data[key] = None
    
   
    file_data = data.get("file", None)
    if file_data and not isinstance(file_data, str):  
        
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        file_extension = os.path.splitext(file_data.name)[1]
        new_filename = f"blog_{current_date}{file_extension}"
        
       
        filtered_data["file"] = file_data
        filtered_data["file"].name = new_filename

    print('filtered_data:', filtered_data)

   
    if 'image' in filtered_data and isinstance(filtered_data['image'], str):
        filtered_data.pop('image')  
    
    if 'meta_image' in filtered_data and isinstance(filtered_data['meta_image'], str):
        filtered_data.pop('meta_image')
        
    if 'fb_meta_image' in filtered_data and isinstance(filtered_data['fb_meta_image'], str):
        filtered_data.pop('fb_meta_image')
        
    serializer = BlogSerializer(blog_instance, data=filtered_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBlog(request, pk):
    try:
        blog_instance = Blog.objects.get(pk=pk)
        blog_instance.delete()
        return Response({'detail': f'Blog id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'detail': f"Blog id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)




# @extend_schema(request=BlogSerializer, responses=BlogSerializer)
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # @has_permissions([PermissionEnum.ATTRIBUTE_DETAILS.name])
# def getBlogByCMSContent(request, pk):
# 	try:
# 		contents = Blog.objects.get(pk=pk)
# 		menu_contents = Blog.objects.filter(cms_content=contents)
# 		serializer = BlogSerializer(menu_contents, many=True)
# 		return Response(serializer.data, status=status.HTTP_200_OK)
# 	except ObjectDoesNotExist:
# 		return Response({'detail': f"Blog id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def searchBlog(request):
    company_id = request.query_params.get('company_id')
    blogs = BlogFilter(request.GET, queryset=Blog.objects.filter(company=company_id).all())
    blogs = blogs.qs

    print('searched_blogs: ', blogs)

    total_elements = blogs.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    blogs = pagination.paginate_data(blogs)

    serializer = BlogListSerializer(blogs, many=True)

    response = {
        'blogs': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }

    if len(blogs) > 0:
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'detail': f"There are no blogs matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def getBlogByTitleSlug(request, slug):
    try:
        company_id = request.query_params.get('company_id')
        print("slug : ", slug)
        content = Blog.objects.filter(company=company_id, slug=slug).first()
        print("content : ", content)
        
        serializer = BlogListSerializer(instance=content)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ObjectDoesNotExist:
        return Response({'detail': f"Blog by title '{slug}' does not exist"}, 
            status=status.HTTP_404_NOT_FOUND)
    

      
@api_view(['POST'])
def uploadImage(request):
    # Check if the file is provided in the request
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    image_field = request.FILES['file']  # Get the uploaded file

    endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
    headers = {
        'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
    }
    files = {
        'file': (image_field.name, image_field.file, image_field.content_type)  # Pass the file name, file object, and content type
    }

    try:
        # Make the POST request to Cloudflare
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        json_data = response.json()
        # print('response',response,'json_data',json_data)
        return Response(json_data, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        # Handle errors from the API request
        return Response({"error": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)