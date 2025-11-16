from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.contrib.auth.models import User

class CertificateRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificate_requests", null=True)
    certificate_type = models.CharField(max_length=50)
    request_number = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    complete_address = models.TextField()
    houseNum = models.PositiveIntegerField(null=True, blank=True)
    contact_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    purpose = models.TextField()
    agree_terms = models.BooleanField(default=False)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
        ],
        default="pending"
    )
    created_at = models.DateTimeField(default=timezone.now)

    CERTIFICATE_PREFIXES = {
    "Certificate of Residency": "CR",
    "Certificate of Indigency": "CI",
    "Business Clearance": "BC",
        }
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.certificate_type == "Business Clearance" and not self.business_name:
            raise ValidationError({"business_name": "Business name is required for Business Clearance."})

    def save(self, *args, **kwargs):
        if not self.request_number:
            prefix = self.CERTIFICATE_PREFIXES.get(self.certificate_type, self.certificate_type[:2].upper())
            with transaction.atomic():
                existing_numbers = (
                    CertificateRequest.objects
                    .filter(certificate_type=self.certificate_type)
                    .values_list('request_number', flat=True)
                )
                
                numbers = []
                for rn in existing_numbers:
                    try:
                        numbers.append(int(rn.split('-')[1]))
                    except (IndexError, ValueError):
                        continue
                next_number = max(numbers, default=0) + 1
                self.request_number = f"{prefix}-{next_number:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} - {self.first_name} {self.last_name}"

    def get_user_birthdate(self):
        if self.user and hasattr(self.user, 'profile'):
            return self.user.profile.birthdate
        return None

    def user_age(self):
        if self.user and hasattr(self.user, 'profile'):
            today = timezone.now().date()
            birthdate = self.user.profile.birthdate
            return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return None

class CertificateCounter(models.Model):
    certificate_type = models.CharField(max_length=50, unique=True)
    last_number = models.PositiveIntegerField(default=0)

class BusinessPermit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_permits", null=True)
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=255)
    business_address = models.TextField()
    contact_number = models.CharField(max_length=20)
    owner_address = models.TextField()
    houseNum = models.PositiveIntegerField(null=True, blank=True)
    business_description = models.TextField(blank=True)
    is_renewal = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name
