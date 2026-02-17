from rest_framework import serializers
from .models import HotelDataModel, Booking  # Import Booking
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class HotelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelDataModel
        fields = [
            'name', 'city', 'area', 'badge',
            # [NEW] Add total_rooms here
            'price', 'old_price', 'total_rooms', 'description','amenities', 'image', 
            'room_image1', 'room_image2', 'environment_image'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        return HotelDataModel.objects.create(owner=user, **validated_data)

class HotelListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.username", read_only=True)
    amenities = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    room_image1 = serializers.SerializerMethodField()
    room_image2 = serializers.SerializerMethodField()
    environment_image = serializers.SerializerMethodField()

    class Meta:
        model = HotelDataModel
        fields = [
            'id',
            'owner',
            'name',
            'city',
            'area',
            'badge',
            'price',
            'old_price',
            'total_rooms',
            'description',
            'amenities',
            'image',
            'room_image1',
            'room_image2',
            'environment_image',
        ]
    
    def get_amenities(self, obj):
        if obj.amenities:
            # Split by comma and strip whitespace
            return [a.strip() for a in obj.amenities.split(',') if a.strip()]
        return []

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_room_image1(self, obj):
        request = self.context.get("request")
        if obj.room_image1 and request:
            return request.build_absolute_uri(obj.room_image1.url)
        return None

    def get_room_image2(self, obj):
        request = self.context.get("request")
        if obj.room_image2 and request:
            return request.build_absolute_uri(obj.room_image2.url)
        return None

    def get_environment_image(self, obj):
        request = self.context.get("request")
        if obj.environment_image and request:
            return request.build_absolute_uri(obj.environment_image.url)
        return None


# [NEW] Serializer for Booking
class BookingSerializer(serializers.ModelSerializer):
    # Nested serializer to get full hotel details (Read Only)
    hotel_details = HotelListSerializer(source='hotel', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'hotel', 'hotel_details', 'check_in', 'check_out', 'status', 'number_of_guests', 'rooms_booked']
        read_only_fields = ['user', 'status', 'rooms_booked']

    def validate(self, data):
        """
        Check if room is available for the given dates.
        """
        hotel = data['hotel']
        check_in = data['check_in']
        check_out = data['check_out']
        number_of_guests = data.get('number_of_guests', 2)

        if check_in >= check_out:
            raise serializers.ValidationError("Check-out date must be after check-in.")

        # 1. Calculate rooms needed for THIS booking (1 room per 2 guests)
        # Use provided 'rooms_booked' or calculate minimum from guests (1 room per 2 guests)
        requested_rooms = data.get('rooms_booked')
        import math
        min_rooms = math.ceil(number_of_guests / 2)

        if not requested_rooms or requested_rooms < min_rooms:
            requested_rooms = min_rooms
            data['rooms_booked'] = requested_rooms # Ensure it's saved correctly

        # 2. Get total rooms for this hotel
        total_rooms = hotel.total_rooms

        if total_rooms > 0:
            # 3. Sum rooms already booked for overlapping dates
            from django.db.models import Sum
            overlapping_rooms = Booking.objects.filter(
                hotel=hotel,
                status='confirmed'
            ).filter(
                # Logic: (StartA < EndB) and (EndA > StartB)
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
            ).aggregate(total=Sum('rooms_booked'))['total'] or 0

            # 4. Check if enough rooms are left
            available_now = total_rooms - overlapping_rooms
            if requested_rooms > available_now:
                raise serializers.ValidationError(
                    f"Only {available_now} rooms are available for these dates. You requested {requested_rooms}."
                )

        return data