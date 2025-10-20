import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tour.models import Tour
from tour.serializers.tour_content_serializers import TourListSerializer, TourSerializer
from datetime import datetime

@api_view(['POST'])
def createTour(request):
    print("Creating a new tour...")

    # make mutable copy
    data = request.data.copy()
    print("Requested form-data:", data)
    print('\n')

    # convert to normal dict
    processed_data = dict(data)

    # single value fields (unwrap list → str)
    for key, value in processed_data.items():
        if isinstance(value, list) and key != "day_tour_price_list" and key != "itineraries_list" and key != "cancellation_policies_list":
            processed_data[key] = value[0]

    # day_tour_price_list handle
    if "day_tour_price_list" in data:
        try:
            processed_data["day_tour_price_list"] = json.loads(data.get("day_tour_price_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in day_tour_price_list"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    # itineraries_list handle
    if "itineraries_list" in data:
        try:
            processed_data["itineraries_list"] = json.loads(data.get("itineraries_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in itineraries_list"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # cancellation_policies_list handle
    if "cancellation_policies_list" in data:
        try:
            processed_data["cancellation_policies_list"] = json.loads(data.get("cancellation_policies_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in cancellation_policies_list"},
                status=status.HTTP_400_BAD_REQUEST)



    # file fields (image etc.)
    if "thumbnail_image" in request.FILES:
        processed_data["thumbnail_image"] = request.FILES["thumbnail_image"]
    
    for key, value in processed_data.items():
        i = 0
        if key.startswith("images[0]"):
            processed_data[f"images[0][{i}]"] = request.FILES[f"images[0][{i}]"]
        i += 1

    print("Processed form-data:", processed_data)
    print('\n')


    serializer = TourSerializer(data=processed_data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        print("Tour created successfully:", serializer.data)
        print('\n')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    print("Tour creation failed:", serializer.errors)
    print('\n')

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def getAllTour(request):
    """
    Retrieve all tours.
    """
    print("Fetching all tours...")
    tours = Tour.objects.all()
    serializer = TourListSerializer(tours, many=True)
    # print("All tours retrieved:", serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getATour(request, pk):
    """
    Retrieve a specific tour by its primary key.
    """
    print(f"Fetching tour with ID: {pk}")
    try:
        tour = Tour.objects.get(pk=pk)
    except Tour.DoesNotExist:
        print("Tour not found.")
        return Response({"error": "Tour not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = TourListSerializer(tour)
    # print("Tour retrieved successfully:", serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def updateTour(request, pk):
    """
    Update a specific tour by its primary key.
    """
    print(f"Updating tour with ID: {pk}")
    # Fetch the tour object to update
    try:
        tour = Tour.objects.get(pk=pk)
    except Tour.DoesNotExist:
        return Response({"error": "Tour not found"}, status=status.HTTP_404_NOT_FOUND)
    print("Tour found for update:", tour)


    # Process the request data
    data = request.data
    print('\n')
    print("Requested form-data for update:", data)
    print('\n')

    # make mutable copy
    data = data.copy()
    # convert to normal dict
    processed_data = dict(data) 
    print("processed data for update:", processed_data)
    print('\n')


    # single value fields (unwrap list → str)
    for key, value in processed_data.items():
        if isinstance(value, list) and key != "day_tour_price_list" and key != "itineraries_list" and key != "cancellation_policies_list":
            processed_data[key] = value[0]


    # day_tour_price_list handle
    if "day_tour_price_list" in data:
        try:
            processed_data["day_tour_price_list"] = json.loads(data.get("day_tour_price_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in day_tour_price_list"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # itineraries_list handle
    if "itineraries_list" in data:
        try:
            processed_data["itineraries_list"] = json.loads(data.get("itineraries_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in itineraries_list"},
                status=status.HTTP_400_BAD_REQUEST)
    
    # cancellation_policies_list handle
    if "cancellation_policies_list" in data:
        try:
            processed_data["cancellation_policies_list"] = json.loads(data.get("cancellation_policies_list"))
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON in cancellation_policies_list"},
                status=status.HTTP_400_BAD_REQUEST)
            
    # handle thumbnail image
    if "thumbnail_image" in request.FILES:
        processed_data["update_thumbnail_image"] = True
        processed_data["thumbnail_image"] = request.FILES["thumbnail_image"]

    # handle images
    for key, value in processed_data.items():
        i = 0
        if key.startswith("images[0]"):
            processed_data[f"images[0][{i}]"] = request.FILES[f"images[0][{i}]"]
        i += 1
    print("Processed form-data for update:", processed_data)

    serializer = TourSerializer(instance=tour, data=processed_data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        print("Tour updated successfully:", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    print("Tour update failed:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # return Response({"message": "Update functionality is not implemented yet."}, status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['DELETE'])
def deleteTour(request, pk):
    """
    Delete a specific tour by its primary key.
    """
    print(f"Deleting tour with ID: {pk}")
    try:
        tour = Tour.objects.get(pk=pk)
    except Tour.DoesNotExist:
        return Response({"error": "Tour not found"}, status=status.HTTP_404_NOT_FOUND)
    tour.delete()
    print(f"Tour {pk} deleted successfully.")
    return Response({"message": f"Tour {pk} deleted successfully!"}, status=204)
    
