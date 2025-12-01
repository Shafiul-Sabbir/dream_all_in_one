from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from commons.pagination import Pagination
from tour.models import OldAgentBooking
from tour.serializers.old_agent_booking_serializers import OldAgentBookingListSerializer


@api_view(['GET'])
def getAnOldAgentBooking(request, pk):
    print("pk is :", pk)
    try:
        booking_instance = OldAgentBooking.objects.get(id=pk)
        print("booking instance:", booking_instance)

        serializer = OldAgentBookingListSerializer(instance=booking_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except OldAgentBooking.DoesNotExist:
        return Response(
            {"error": f"No booking instance found for id {pk}"},
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['GET'])
def getAllOldAgentBooking(request):
    tour_bookings = OldAgentBooking.objects.all()
    total_elements = tour_bookings.count()
    serializer = OldAgentBookingListSerializer(tour_bookings, many=True)
    response = {
        'old_agent_bookings': serializer.data,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
def getAllOldAgentBookingByCompanyID(request):
    company_id = request.query_params.get('company_id')
    tour_bookings = OldAgentBooking.objects.filter(company=company_id).all()
    total_elements = tour_bookings.count()
    serializer = OldAgentBookingListSerializer(tour_bookings, many=True)
    response = {
        'old_agent_bookings': serializer.data,
        'total_elements': total_elements,
    }
    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getAllOldAgentBookingByCompanyIDWithPagination(request):
    company_id = request.query_params.get('company_id')
    tour_bookings = OldAgentBooking.objects.filter(company=company_id).all()
    total_elements = tour_bookings.count()

    page = request.query_params.get('page')
    size = request.query_params.get('size')

    # Pagination
    pagination = Pagination()
    pagination.page = page
    pagination.size = size
    tour_bookings = pagination.paginate_data(tour_bookings)

    serializer = OldAgentBookingListSerializer(tour_bookings, many=True)
    response = {
        'old_agent_bookings': serializer.data,
        'total_elements': total_elements,
        'page': pagination.page,
        'size': pagination.size,
        'total_pages': pagination.total_pages,
    }
    return Response(response, status=status.HTTP_200_OK)