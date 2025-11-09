from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from cms.models import Review
from cms.serializers import  ReviewListSerializer
from cms.filters import *
from commons.pagination import Pagination
import os

# Create your views here.
@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=ReviewListSerializer,
	responses=ReviewListSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.ATTRIBUTE_LIST.name])

def getAllReview(request):

    company_id = request.query_params.get('company_id')
    page = request.query_params.get('page')
    size = request.query_params.get('size')

    reviews = Review.objects.filter(company=company_id).all()
    # reviews = Review.objects.all().select_related('created_by', 'updated_by')
    """
    Ekhane Review model e sudhu 'created_by' ebong 'updated_by' duita ForeignKey field ache. 
    Amader dataset currently chhoto bole normal queryset (Review.objects.all()) use korei efficiently 
    data load kora jacche. select_related() use korle created_by ebong updated_by er shathe join hoy, 
    jeta large dataset e extra overhead create korte pare, jodi oi related user data actually lagena.

    Tobe, jodi serializer e created_by.email or updated_by.email field access kora hoy (as in our case), 
    tahole select_related() use korle N+1 query problem avoid kora jai — mane ekta query diyei related user 
    data nia asha jai, bar bar separate query na kore.

    So, current chhoto dataset er jonno select_related() optional, but user info dorkar hole helpful.
    """
    # print("reviews : ", reviews)
    total_elements = reviews.count()

     # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    reviews = pagination.paginate_data(reviews)

    serializer = ReviewListSerializer(reviews, many=True)

    response = {
        'reviews': serializer.data,        
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllReviewWithoutPagination(request):
    company_id = request.query_params.get('company_id')
    reviews = Review.objects.filter(company=company_id).all()
    # print("reviews : ", reviews)
    total_elements = reviews.count()

    serializer = ReviewListSerializer(reviews, many=True)

    response = {
        'reviews': serializer.data,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)




