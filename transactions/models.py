from django.db import models
from django.utils import timezone
from customers.models import Customer


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('due', 'Due'),
        ('paid', 'Paid'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.FloatField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    reason = models.TextField(null=True, blank=True)
    running_balance = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        return f"{self.customer.name} | {self.get_type_display()} | ₹{self.amount}"
