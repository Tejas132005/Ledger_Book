from django.urls import path
from .views import CustomerRegisterView, CustomerLoginView, GeneratePDFView

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('download-pdf/<int:customer_id>/', GeneratePDFView.as_view(), name='download_pdf'),
]
