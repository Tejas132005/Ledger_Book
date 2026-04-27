from django.urls import path
from .views import (
    CustomerRegisterView, CustomerLoginView, GeneratePDFView,
    CustomerListView, CustomerUpdateView, CustomerDeleteView
)

urlpatterns = [
    path('list/', CustomerListView.as_view(), name='customer_list'),
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('edit/<int:pk>/', CustomerUpdateView.as_view(), name='customer_edit'),
    path('delete/<int:pk>/', CustomerDeleteView.as_view(), name='customer_delete'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('download-pdf/<int:customer_id>/', GeneratePDFView.as_view(), name='download_pdf'),
]
