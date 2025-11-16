from django.contrib import admin
from .models import CertificateRequest, BusinessPermit
# Register your models here.

admin.site.register(CertificateRequest)
admin.site.register(BusinessPermit)
