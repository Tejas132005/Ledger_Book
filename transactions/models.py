from django.db import models
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
    date_time = models.DateTimeField(auto_now_add=True)
    running_balance = models.FloatField(default=0)

    class Meta:
        ordering = ['date_time', 'id']

    def __str__(self):
        return f"{self.customer.name} | {self.get_type_display()} | ₹{self.amount}"
