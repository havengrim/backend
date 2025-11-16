from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from . import views
def health_check(request):
    return JsonResponse({"status": "ok"})
urlpatterns = [
    path('', health_check),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/announcements/', include('announcements.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/emergencies/', include('emergency.urls')),
    path('api/blotters/', include('blotter.urls')),
    path('export-report/', views.export_all_reports_excel, name='export_report'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
