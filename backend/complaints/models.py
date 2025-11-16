from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from emergency.storages import SupabaseStorage

supabase_storage = SupabaseStorage()
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints', null=True)
    type = models.CharField(max_length=100)
    fullname = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    email_address = models.EmailField()
    subject = models.CharField(max_length=200)
    detailed_description = models.TextField()
    respondent_name = models.CharField(max_length=150)
    respondent_address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    date_filed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    priority = models.CharField(max_length=50, default='medium')
    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    evidence = models.FileField(storage=supabase_storage,upload_to='complaint_evidence/', null=True, blank=True)

    def __str__(self):
        return f"{self.subject} by {self.fullname}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)  # Save first to get an ID
            self.reference_number = f"CM-{timezone.now().year}-{str(self.id).zfill(6)}"
            return super().save(update_fields=['reference_number']) 
        return super().save(*args, **kwargs)
