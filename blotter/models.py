from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BlotterReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Varies', 'Varies'),
    ]

    # Use the incident types from your React frontend exactly
    INCIDENT_TYPE_CHOICES = [
        ('Noise Complaint', 'Noise Complaint'),
        ('Theft/Burglary', 'Theft/Burglary'),
        ('Neighbor Dispute', 'Neighbor Dispute'),
        ('Traffic Violation', 'Traffic Violation'),
        ('Property Damage', 'Property Damage'),
        ('Others', 'Others'),
    ]

    report_number = models.AutoField(primary_key=True)
    filed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blotter_filed')

    complainant_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    respondent_name = models.CharField(max_length=255, blank=True, null=True)

    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPE_CHOICES)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    witnesses = models.TextField(blank=True, null=True)
    agree_terms = models.BooleanField(default=False)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    resolution_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Blotter #{self.report_number} - {self.incident_type} - {self.complainant_name}"
