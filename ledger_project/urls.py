from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from customers.views import AdminDashboardView, CustomerTransactionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', AdminDashboardView.as_view(), name='dashboard'),
    path('home/', AdminDashboardView.as_view(), name='dashboard_home'),
    path('accounts/', include('accounts.urls')),
    path('customers/', include('customers.urls')),
    path('transactions/', include('transactions.urls')),
    # Customer transaction page by ID
    path('customer/<int:customer_id>/transactions/', CustomerTransactionView.as_view(), name='customer_transactions'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
