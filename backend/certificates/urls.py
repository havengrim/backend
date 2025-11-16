from django.urls import path
from .views import (
    CertificateRequestCreateView,
    CertificateRequestListView,
    CertificateRequestDetailView,
    CertificateRequestUpdateView,
    CertificateRequestDeleteView,
    BusinessPermitListCreateView,
    BusinessPermitRetrieveUpdateDestroyView
)

urlpatterns = [
 path('', CertificateRequestListView.as_view(), name='certificate-list'),  # GET /api/certificates/
    path('create/', CertificateRequestCreateView.as_view(), name='certificate-create'),  # POST /api/certificates/create/
    path('<int:id>/', CertificateRequestDetailView.as_view(), name='certificate-detail'),  # GET /api/certificates/4/
    path('edit/<int:id>/', CertificateRequestUpdateView.as_view(), name='certificate-edit'),  # PUT /api/certificates/edit/4/
    path('delete/<int:id>/', CertificateRequestDeleteView.as_view(), name='certificate-delete'),  # DELETE /api/certificates/delete/4/
    path('business-permits/', BusinessPermitListCreateView.as_view(), name='business-permit-list-create'),
    path('business-permits/<int:pk>/', BusinessPermitRetrieveUpdateDestroyView.as_view(), name='business-permit-detail'),
]
