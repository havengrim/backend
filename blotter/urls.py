from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlotterReportViewSet

router = DefaultRouter()
router.register(r'', BlotterReportViewSet, basename='blotterreport')


urlpatterns = [
    path('', include(router.urls)),
]
