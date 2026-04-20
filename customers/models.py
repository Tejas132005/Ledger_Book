from django.db import models
from django.conf import settings


class Customer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customers'
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'phone_number')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def get_balance(self):
        last_tx = self.transactions.order_by('date', 'id').last()
        return last_tx.running_balance if last_tx else 0
