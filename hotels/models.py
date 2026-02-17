from django.db import models
from django.contrib.auth import get_user_model

# Get the user model (works with custom User models too)
User = get_user_model()

class HotelDataModel(models.Model):
    BADGE_CHOICES = [
        ('Luxury Stays', 'Luxury Stays'),
        ('Cheap & Best', 'Cheap & Best'),
        ('Dormitory', 'Dormitory'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hotels',
        null=True,  # allow NULL temporarily if needed during migration
        blank=True
    )
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # [NEW] Field to track how many rooms exist for this hotel entry
    total_rooms = models.PositiveIntegerField(
        default=1, 
        help_text="Total number of rooms available for this hotel/category"
    )

    description = models.TextField()
    amenities = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='hotels/')
    room_image1 = models.ImageField(upload_to='hotels/rooms/', blank=True, null=True)
    room_image2 = models.ImageField(upload_to='hotels/rooms/', blank=True, null=True)
    environment_image = models.ImageField(upload_to='hotels/environment/', blank=True, null=True)

    def __str__(self):
        return self.name


# [NEW] Booking Model for handling reservations
class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    hotel = models.ForeignKey(
        HotelDataModel, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    number_of_guests = models.PositiveIntegerField(default=2)
    rooms_booked = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate rooms needed if not provided or too low (2 guests per room)
        import math
        min_rooms = math.ceil(self.number_of_guests / 2)
        if not self.rooms_booked or self.rooms_booked < min_rooms:
            self.rooms_booked = min_rooms
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.hotel.name} ({self.rooms_booked} rooms, {self.number_of_guests} guests)"