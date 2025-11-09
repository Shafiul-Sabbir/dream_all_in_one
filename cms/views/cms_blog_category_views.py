from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from cms.models import BlogCategory
from cms.serializers import BlogCategorySerializer, BlogCategoryListSerializer
from cms.filters import BlogCategoryFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination
import os



# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		
		OpenApiParameter("size"),
  ],
	request=BlogCategorySerializer,
	responses=BlogCategorySerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_LIST_VIEW.name])
def getAllBlogCategory(request):
	company_id = request.query_params.get('company_id')
	blog_categories = BlogCategory.objects.filter(company=company_id).all()
	total_elements = blog_categories.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	blog_categories = pagination.paginate_data(blog_categories)

	serializer = BlogCategoryListSerializer(blog_categories, many=True)

	response = {
		'blog_categories': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllBlogCategoryWithoutPagination(request):
	company_id = request.query_params.get('company_id')
	blog_categories = BlogCategory.objects.filter(company=company_id).all()
	total_elements = blog_categories.count()

	serializer = BlogCategoryListSerializer(blog_categories, many=True)

	return Response({
		'total_elments' : total_elements,
		'blog_categories': serializer.data
		}, status=status.HTTP_200_OK)




@extend_schema(request=BlogCategorySerializer, responses=BlogCategorySerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def getABlogCategory(request, pk):
	try:
		blog_categories = BlogCategory.objects.get(pk=pk)
		serializer = BlogCategorySerializer(blog_categories)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"BlogCategory id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=BlogCategorySerializer, responses=BlogCategorySerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchBlogCategory(request):
	company_id = request.query_params.get('company_id')
	blog_categories = BlogCategoryFilter(request.GET, queryset=BlogCategory.objects.filter(company=company_id).all())
	blog_categories = blog_categories.qs

	print('searched_products: ', blog_categories)

	total_elements = blog_categories.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	blog_categories = pagination.paginate_data(blog_categories)

	serializer = BlogCategoryListSerializer(blog_categories, many=True)

	response = {
		'blog_categories': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(blog_categories) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no blog_categories matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=BlogCategorySerializer, responses=BlogCategorySerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_CREATE.name])
def createBlogCategory(request):
	data = request.data
	filtered_data = {}

	for key, value in data.items():
		if value != '' and value != '0':
			filtered_data[key] = value

	serializer = BlogCategorySerializer(data=filtered_data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=BlogCategorySerializer, responses=BlogCategorySerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_UPDATE.name, PermissionEnum.PERMISSION_PARTIAL_UPDATE.name])
def updateBlogCategory(request,pk):
	try:
		blog_categories = BlogCategory.objects.get(pk=pk)
		data = request.data
		serializer = BlogCategorySerializer(blog_categories, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"BlogCategory id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=BlogCategorySerializer, responses=BlogCategorySerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DELETE.name])
def deleteBlogCategory(request, pk):
	try:
		blog_categories = BlogCategory.objects.get(pk=pk)
		blog_categories.delete()
		return Response({'detail': f'BlogCategory id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"BlogCategory id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

