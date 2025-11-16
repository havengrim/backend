from django.db import models
from django.utils import timezone
from .storages import SupabaseStorage


class EmergencyReport(models.Model):
    INCIDENT_TYPES = [
        ('fire', 'Fire'),
        ('medical', 'Medical'),
        ('security', 'Security'),
        ('flood', 'Flood'),
        ('earthquake', 'Earthquake'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES, default='other')
    description = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0.0, null=True)
    alert_message = models.TextField(default="🚨 Emergency reported. Stay alert.")

    # Optional media upload (image/audio/video)
    media_file = models.FileField(
        storage=SupabaseStorage,  # Use class, not instance
        upload_to='emergency_media/',
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Location fields
    location_text = models.CharField(max_length=255)  # e.g., "123 Main St" or "Near City Park"

    # Contact phone number
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    submitted_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.incident_type} at {self.location_text} ({self.status})"


class EmergencyAlert(models.Model):
    type = models.CharField(max_length=100, unique=True)  # e.g., 'rape', 'thief', 'fire'
    alert_message = models.TextField(default="🚨 Emergency reported. Stay alert.")
    # e.g., '🚨 Theft incident reported nearby. Secure your belongings.'

    def __str__(self):
        return self.type
