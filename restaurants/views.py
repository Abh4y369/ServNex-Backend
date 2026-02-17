from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RestaurantDataModel, TableReservation
from .serializers import RestaurantSerializer, TableReservationSerializer


class RestaurantListCreateView(generics.ListCreateAPIView):
    """
    GET: List all restaurants
    POST: Create a new restaurant (business owners only)
    """
    queryset = RestaurantDataModel.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Authenticated users can create, anyone can view

    def perform_create(self, serializer):
        # Automatically set the owner to the logged-in user
        serializer.save(owner=self.request.user)


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific restaurant
    PUT/PATCH: Update restaurant details (owner only)
    DELETE: Delete restaurant (owner only)
    """
    queryset = RestaurantDataModel.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view

    def get_permissions(self):
        # Only owner can update/delete
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class TableReservationListCreateView(generics.ListCreateAPIView):
    """
    GET: List all reservations (admin only)
    POST: Create a new reservation (authenticated users)
    """
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)


class UserReservationsView(generics.ListAPIView):
    """
    GET: List all reservations for the logged-in user
    """
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user)


class RestaurantReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific reservation
    PUT/PATCH: Update reservation (user who made it only)
    DELETE: Cancel reservation (user who made it only)
    """
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only access their own reservations
        return TableReservation.objects.filter(user=self.request.user)
