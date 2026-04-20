from django.urls import path
from .views import AddTransactionView, DeleteTransactionView, GetBalanceAPIView, UpdateReasonView

urlpatterns = [
    path('add/<int:customer_id>/', AddTransactionView.as_view(), name='add_transaction'),
    path('delete/<int:pk>/', DeleteTransactionView.as_view(), name='delete_transaction'),
    path('update-reason/<int:pk>/', UpdateReasonView.as_view(), name='update_reason'),
    path('api/balance/<int:customer_id>/', GetBalanceAPIView.as_view(), name='get_balance_api'),
]
