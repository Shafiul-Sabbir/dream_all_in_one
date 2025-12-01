from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import  extend_schema, OpenApiParameter
from cms.models import Review
from cms.serializers import  ReviewListSerializer, ReviewSerializer
from cms.filters import *
from commons.pagination import Pagination
import os

# Create your views here.
@api_view(['GET'])
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createReview(request):
    data = request.data
    print('data: ', data)
    
    serializer = ReviewSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateReview(request, pk):
    data = request.data
    print('data: ', data)

    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(review, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteReview(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return Response({'message': 'Review deleted successfully'}, status=status.HTTP_200_OK)  



