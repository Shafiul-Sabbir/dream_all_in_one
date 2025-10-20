from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from commons.pagination import Pagination
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, time
from django.utils import timezone
from tour.models import CancellationPolicy
from tour.serializers.tour_content_serializers import CancellationPolicySerializer, CancellationPolicyListSerializer
from tour.models import Tour
@api_view(['POST'])
def createTourCancellationPolicy(request):
    print("Creating a new Cancellation Policy...")
    tour_id = 49
    tour = Tour.objects.get(id=tour_id)
    data = request.data
    # print("Requested data:", data)
    for object in data:
        print('\n')
        print(type(object))
        print(object)
        print('\n')
        for key, value in object.items():
            print(f"{key}: {value}")
        print('\n')
        object['tour'] = tour.id
        print("creating Cancellation Policy for Tour ID:", tour_id)
        serializer = CancellationPolicySerializer(data=object)
        if serializer.is_valid():
            serializer.save()
            print("Saved object:", serializer.data)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    print('\n')

    return Response({"message": "Successfully created all Cancellation Policies"}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
def updateTourCancellationPolicyByPolicyId(request, policy_id):
    print("Updating Cancellation Policy ID:", policy_id)
    try:
        cancellation_policy = CancellationPolicy.objects.get(id=policy_id)
    except ObjectDoesNotExist:
        return Response({"error": "Cancellation Policy not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CancellationPolicySerializer(cancellation_policy, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def getAllTourCancellationPoliciesByTourId(request, tour_id):
    print("Fetching all Cancellation Policies for Tour ID:", tour_id)
    try:
        tour = Tour.objects.get(id=tour_id)
    except ObjectDoesNotExist:
        return Response({"error": "Tour not found."}, status=status.HTTP_404_NOT_FOUND)

    cancellation_policies = CancellationPolicy.objects.filter(tour=tour)
    if not cancellation_policies.exists():
        return Response({"message": "No Cancellation Policies found for this Tour."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CancellationPolicyListSerializer(cancellation_policies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getATourCancellationPolicyByPolicyId(request, policy_id):
    print("Fetching Cancellation Policy ID:", policy_id)
    try:
        cancellation_policy = CancellationPolicy.objects.get(id=policy_id)
    except ObjectDoesNotExist:
        return Response({"error": "Cancellation Policy not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CancellationPolicyListSerializer(cancellation_policy)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def deleteTourCancellationPolicyByPolicyId(request, policy_id):
    print("Deleting Cancellation Policy ID:", policy_id)
    try:
        cancellation_policy = CancellationPolicy.objects.get(id=policy_id)
    except ObjectDoesNotExist:
        return Response({"error": "Cancellation Policy not found."}, status=status.HTTP_404_NOT_FOUND)

    cancellation_policy.delete()
    return Response({"message": "Cancellation Policy deleted successfully."}, status=status.HTTP_200_OK)