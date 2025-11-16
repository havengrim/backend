from django.contrib import admin
from .models import EmergencyReport, EmergencyAlert

# Register both models
admin.site.register(EmergencyReport)
admin.site.register(EmergencyAlert)
