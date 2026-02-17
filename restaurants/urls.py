from django.urls import path
from .views import (
    RestaurantListCreateView,
    RestaurantDetailView,
    TableReservationListCreateView,
    UserReservationsView,
    RestaurantReservationDetailView
)

urlpatterns = [
    # Restaurant endpoints
    path('restaurants/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    
    # Reservation endpoints
    path('reservations/', TableReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', RestaurantReservationDetailView.as_view(), name='reservation-detail'),
    path('my-reservations/', UserReservationsView.as_view(), name='user-reservations'),
]
