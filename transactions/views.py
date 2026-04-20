from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from customers.models import Customer
from .models import Transaction


class AddTransactionView(View):
    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)

        try:
            amount = float(request.POST.get('amount', 0))
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount.")
            return redirect('customer_transactions', customer_id=customer.id)

        tx_type = request.POST.get('type', 'due')

        if amount <= 0:
            messages.error(request, "Amount must be greater than ₹0.")
            return redirect('customer_transactions', customer_id=customer.id)

        if tx_type not in ('due', 'paid'):
            messages.error(request, "Invalid transaction type.")
            return redirect('customer_transactions', customer_id=customer.id)

        current_balance = customer.get_balance()

        if tx_type == 'due':
            new_balance = current_balance + amount
        else:
            new_balance = current_balance - amount

        Transaction.objects.create(
            customer=customer,
            type=tx_type,
            amount=amount,
            running_balance=new_balance
        )

        action = "added as DUE" if tx_type == 'due' else "received as PAYMENT"
        messages.success(request, f"₹{amount:.2f} {action}. New balance: ₹{new_balance:.2f}")
        return redirect('customer_transactions', customer_id=customer.id)


class DeleteTransactionView(View):
    def post(self, request, pk):
        tx = get_object_or_404(Transaction, pk=pk)
        customer = tx.customer

        # Delete this transaction and all subsequent ones (cascade forward)
        Transaction.objects.filter(
            customer=customer,
            date_time__gte=tx.date_time,
            id__gte=tx.id
        ).delete()

        messages.warning(request, "Transaction and all subsequent entries have been deleted.")
        return redirect('customer_transactions', customer_id=customer.id)


class GetBalanceAPIView(View):
    """Simple JSON endpoint to get current balance for JS confirmation dialog."""
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        return JsonResponse({'balance': customer.get_balance()})
