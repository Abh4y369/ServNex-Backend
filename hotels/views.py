from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework import status

from .models import HotelDataModel, Booking # Import Booking
from django.db.models import Q # Import Q
from .serializers import (
    HotelCreateSerializer, 
    HotelListSerializer, 
    BookingSerializer # Import BookingSerializer
)

class HotelListAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = HotelDataModel.objects.all()
    serializer_class = HotelListSerializer # Use ListSerializer for GET requests usually

    def get(self, request):
        hotels = HotelDataModel.objects.all()
        serializer = HotelListSerializer(hotels, many=True, context={'request': request})
        return Response(serializer.data)

class HotelViewSet(ModelViewSet):
    queryset = HotelDataModel.objects.all().order_by('-id')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return HotelCreateSerializer
        return HotelListSerializer

    def get_serializer_context(self):
        return {"request": self.request}


# [NEW] ViewSet for Bookings
class BookingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated] # Only logged in users can book
    serializer_class = BookingSerializer

    def get_queryset(self):
        # Users see only their own bookings
        # Admins (superusers) can see all
        user = self.request.user
        if user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        # The serializer.validate() we wrote earlier handles the availability check!
        serializer.save(user=self.request.user)

    # Optional: Custom action to check availability without booking
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def check_availability(self, request):
        hotel_id = request.query_params.get('hotel_id')
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not all([hotel_id, check_in, check_out]):
            return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            hotel = HotelDataModel.objects.get(id=hotel_id)
        except HotelDataModel.DoesNotExist:
             return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

        # [FIX] If total_rooms is 0, no bookings allowed
        if hotel.total_rooms <= 0:
            return Response({"available": False, "message": "Room is full"})

        # Calculate rooms needed for this booking (2 per room)
        number_of_guests = int(request.query_params.get('number_of_guests', 2))
        import math
        rooms_needed = math.ceil(number_of_guests / 2)

        # Sum total rooms already booked for overlapping dates
        from django.db.models import Sum
        overlapping_rooms = Booking.objects.filter(
            hotel=hotel,
            status='confirmed'
        ).filter(
            Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        ).aggregate(total=Sum('rooms_booked'))['total'] or 0
        
        if overlapping_rooms + rooms_needed > hotel.total_rooms:
             return Response({"available": False, "message": "Room is full"})
        
        return Response({"available": True, "message": "Room available"})
    

class HotelDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        
        # 1. Find all hotels owned by this user (e.g. "Taj Hotel" owned by User X)
        my_hotels = HotelDataModel.objects.filter(owner=user)
        
        # 2. Find all bookings for THESE hotels
        # e.g. User Y booked "Taj Hotel" -> Show this
        # e.g. User Z booked "Oberoi" (User A owner) -> Hide this
        my_bookings = Booking.objects.filter(hotel__in=my_hotels).select_related('user', 'hotel')
        
        data = []
        for booking in my_bookings:
            data.append({
                "booking_id": booking.id,
                "customer_name": booking.user.username,  # Adjust if using get_full_name()
                "customer_email": booking.user.email,
                "hotel_name": booking.hotel.name,
                "check_in": booking.check_in,
                "check_out": booking.check_out,
                "status": booking.status,
                "booked_at": booking.created_at
            })
            
        return Response(data)