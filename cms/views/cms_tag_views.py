from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from cms.models import Tag
from cms.serializers import TagSerializer, TagListSerializer
from cms.filters import TagFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination




# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		
		OpenApiParameter("size"),
  ],
	request=TagSerializer,
	responses=TagSerializer
)
@api_view(['GET'])
def getAllTag(request):
	company_id = request.query_params.get('company_id')
	tags = Tag.objects.filter(company=company_id).all()
	total_elements = tags.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	tags = pagination.paginate_data(tags)

	serializer = TagListSerializer(tags, many=True)

	response = {
		'tags': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	return Response(response, status=status.HTTP_200_OK)



@api_view(['GET'])
def getAllTagWithoutPagination(request):
	company_id = request.query_params.get('company_id')
	tags = Tag.objects.filter(company=company_id).all()

	serializer = TagListSerializer(tags, many=True)

	return Response({'tags': serializer.data}, status=status.HTTP_200_OK)




@extend_schema(request=TagSerializer, responses=TagSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def getATag(request, pk):
	try:
		tags = Tag.objects.get(pk=pk)
		serializer = TagSerializer(tags)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Tag id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def searchTag(request):
	company_id = request.query_params.get('company_id')
	tags = TagFilter(request.GET, queryset=Tag.objects.filter(company=company_id).all())
	tags = tags.qs

	print('searched_products: ', tags)

	total_elements = tags.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	tags = pagination.paginate_data(tags)

	serializer = TagListSerializer(tags, many=True)

	response = {
		'tags': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(tags) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no tags matching your search"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createTag(request):
	data = request.data
	filtered_data = {}

	for key, value in data.items():
		if value != '' and value != '0':
			filtered_data[key] = value

	serializer = TagSerializer(data=filtered_data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateTag(request,pk):
	try:
		tags = Tag.objects.get(pk=pk)
		data = request.data
		serializer = TagSerializer(tags, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"Tag id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteTag(request, pk):
	try:
		tags = Tag.objects.get(pk=pk)
		tags.delete()
		return Response({'detail': f'Tag id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Tag id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

