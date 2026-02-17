from rest_framework import serializers
from .models import RestaurantDataModel, TableReservation


class RestaurantSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    image = serializers.ImageField(required=False)
    menu_image = serializers.ImageField(required=False)
    interior_image = serializers.ImageField(required=False)

    class Meta:
        model = RestaurantDataModel
        fields = [
            'id', 'owner', 'owner_name', 'name', 'city', 'area', 'badge',
            'cuisine_type', 'price_range', 'average_cost_for_two', 'total_tables',
            'description', 'rating', 'image', 'menu_image', 'interior_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'owner_name']


class TableReservationSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    restaurant_image = serializers.ImageField(source='restaurant.image', read_only=True)

    class Meta:
        model = TableReservation
        fields = [
            'id', 'user', 'user_name', 'restaurant', 'restaurant_name', 
            'restaurant_image', 'reservation_date', 'reservation_time',
            'number_of_guests', 'tables_reserved', 'status', 'special_requests',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'user_name', 'restaurant_name', 
                           'restaurant_image', 'tables_reserved']

    def validate(self, data):
        """
        Check that reservation date is not in the past
        """
        from datetime import date
        if data.get('reservation_date') and data['reservation_date'] < date.today():
            raise serializers.ValidationError("Reservation date cannot be in the past")
        return data
