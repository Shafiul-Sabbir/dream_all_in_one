from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from commons.pagination import Pagination
from tour.models import TourItinerary, Tour
from cms.models import CMSMenu, Itinerary
from tour.serializers.tour_itinerary_serializers import TourItinerarySerializer, TourItineraryListSerializer
from utils.utils import reformed_head_or_name

@api_view(['POST'])
def createItinerary(request):
    data = request.data
    print("data:", data)
    itineraries = data.get('itineraries', [])
    for itinerary_data in itineraries:
        tour_id = itinerary_data.get('tour_id')
        title = itinerary_data.get('title')
        description = itinerary_data.get('description')
        location = itinerary_data.get('location')
        lat = itinerary_data.get('lat')
        long = itinerary_data.get('long')
        if not tour_id or not title:
            return Response({"error": "tour_id and title are required fields."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tour = Tour.objects.get(id=tour_id)
        except Tour.DoesNotExist:
            return Response({"error": f"Tour with id {tour_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        
        validated_data = {
            'tour': tour.id,
            'title': title,
            'description': description,
            'location': location,
            'lat': lat,
            'long': long
        }
        serializer = TourItinerarySerializer(data=validated_data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    return Response({"message": "Itineraries created successfully"}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def updateItinerary(request, pk):
    try:
        itinerary = TourItinerary.objects.get(id = pk)
        print(itinerary)

    except Itinerary.DoesNotExist:
        return Response({"error" : "itinerary not found for this id "})
    
    data = request.data
    validated_data = data.get("itinerary", [])
    print("itinerary : ",  itinerary)
    
    serializer = TourItinerarySerializer(instance=itinerary, data=validated_data)
    if serializer.is_valid():
        serializer.save()
    
    return Response({"result" : "updated successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def getAllItineraryByTourId(resuest, tour_id):
    print("getting tour")
    try:
        tour = Tour.objects.get(id = tour_id)
        # print(tour)

    except Tour.DoesNotExist:
        return Response({"error": "tour not found for this tour id."}, status=status.HTTP_404_NOT_FOUND)
    

    itineraries = tour.itineraries_list.all()
    # print(itineraries)
    serializer = TourItineraryListSerializer(itineraries, many=True)
    # print(serializer)

    
    return Response({
        "status" : "OK",
        "itineraries" : serializer.data,
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
def getAllItinerary(request):
    itineraries= TourItinerary.objects.all()
    total_elements = itineraries.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    menu_items = pagination.paginate_data(itineraries)

    serializer = TourItineraryListSerializer(menu_items, many=True)

    response = {
        'itineraries': serializer.data,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def getAllItineraryWithoutPagination(request):
    itineraries = TourItinerary.objects.all()
    total_elements = itineraries.count()

    serializer = TourItineraryListSerializer(itineraries, many=True)
    response = {
        'itineraries': serializer.data,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def getAItinerary(request, pk):
    try:
        itinerary = TourItinerary.objects.get(pk=pk)
        serializer = TourItinerarySerializer(itinerary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Itinerary.DoesNotExist:
        return Response({'detail': f"Itinerary of id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteItinerary(request, pk):
    try:
        itinerary = TourItinerary.objects.get(pk=pk)
        # serializer = TourItinerarySerializer(itinerary)
        itinerary.delete()
        return Response({"response " : "Itinerary deleted successfully"}, status=status.HTTP_200_OK)
    except Itinerary.DoesNotExist:
        return Response({'detail': f"Itinerary of id - {pk} does't exists"}, status=status.HTTP_400_BAD_REQUEST)

from collections import defaultdict

@api_view(['GET'])
def populateToursWithMenuItineraries(request):
    print('\n')
    print("Populating tours with menu itineraries...")
    full_cms_list = []
    all_cms_itineraries = Itinerary.objects.all()
    for cms_itinerary in all_cms_itineraries:
        cms_content_name = cms_itinerary.cms_content.name
        cms_content_name = reformed_head_or_name(cms_content_name)
        # print(f"cms content name: {cms_content_name}, for cms_itinerary object: {cms_itinerary}" )
        full_cms_list.append((cms_content_name, cms_itinerary))
    
    # print("Full CMS List:", full_cms_list)
    # itinerary of single cms content name
    cms_itinerary_dict = defaultdict(list)    
    seen_titles = defaultdict(set)

    for cms_content_name, cms_itinerary in full_cms_list:
        if cms_itinerary.title not in seen_titles[cms_content_name]:
            seen_titles[cms_content_name].add(cms_itinerary.title)
            cms_itinerary_dict[cms_content_name].append(cms_itinerary)


    tours = Tour.objects.all()
    for tour in tours:
        # print("tour name : ", tour.name)
        pass
    
        # Step 1: Tour dict → {reformed_name: tour_obj}
    tour_dict = {
        reformed_head_or_name(tour.name): tour
        for tour in tours
    }
    print('\n')
    print("CMS Itinerary Dict Keys:", cms_itinerary_dict.keys())
    print("Total unique CMS contents with itineraries:", len(cms_itinerary_dict))
    print('\n')
    # print("tour dict keys: ", tour_dict.keys())
    tour_itineraries = TourItinerary.objects.all()
    tour_itineraries_title_list = []
    for tour_itinerary in tour_itineraries:
        tour_itineraries_title_list.append(tour_itinerary.title)

    for tour_name, tour_obj in tour_dict.items():
        # print(f"tour_name: {tour_name} and tour object {tour_obj}")
        for cms_content_name, itineraries in cms_itinerary_dict.items():
            if tour_name == cms_content_name:
                print(f"Match found for tour: {tour_name}")
                print(f"CMS Content Name: {cms_content_name} has {len(itineraries)} itineraries.")
                for itinerary in itineraries:
                    print(f"cms_menu id {itinerary.cms_content.id}")
                    print(f"- For tour id {tour_obj.id},  Itinerary ID: {itinerary.id}, Title: {itinerary.title}, lat: {itinerary.lat}, long: {itinerary.lng}")
                    if itinerary.title not in tour_itineraries_title_list:
                        tour_itinerary_dict = {
                            'tour': tour_obj.id,
                            'title': itinerary.title,
                            'description': itinerary.description,
                            'location': itinerary.location,
                            'lat': itinerary.lat,
                            'long': itinerary.lng
                        }
                        serializer = TourItinerarySerializer(data=tour_itinerary_dict)
                        if serializer.is_valid():
                            serializer.save()
                            print(f"--> Itinerary '{itinerary.title}' added to tour id '{tour_obj.id}'")
                        else:
                            print(f"Error saving itinerary '{itinerary.title}' for tour '{tour_obj.name}': {serializer.errors}")
                    else:
                        print("skipping for adding itinerary against this tour as this itinerary exists.")
                print('\n')


    print('\n')
    return Response({"message" : " This feature is under development."}, status=status.HTTP_200_OK)