from django.urls import path
from .views import (
    ComplaintCreateView,
    ComplaintListByUserView,
    ComplaintDetailView,
    ComplaintUpdateView,
    ComplaintDeleteView,
    ComplaintListView
)

urlpatterns = [
    path('create/', ComplaintCreateView.as_view(), name='complaint-create'),
    path('', ComplaintListView.as_view(), name='complaint-list'),
    path('my-complaints/', ComplaintListByUserView.as_view(), name='complaint-list-by-user'),
    path('<int:id>/', ComplaintDetailView.as_view(), name='complaint-detail'),
    path('<int:id>/update/', ComplaintUpdateView.as_view(), name='complaint-update'),
    path('<int:id>/delete/', ComplaintDeleteView.as_view(), name='complaint-delete'),
]