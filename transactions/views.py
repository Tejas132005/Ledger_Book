from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
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
        tx_date_str = request.POST.get('date')
        reason = request.POST.get('reason', '')

        if amount <= 0:
            messages.error(request, "Amount must be greater than ₹0.")
            return redirect('customer_transactions', customer_id=customer.id)

        if tx_type not in ('due', 'paid', 'interest'):
            messages.error(request, "Invalid transaction type.")
            return redirect('customer_transactions', customer_id=customer.id)

        if not tx_date_str:
            messages.error(request, "Date is required.")
            return redirect('customer_transactions', customer_id=customer.id)

        try:
            tx_date = timezone.datetime.strptime(tx_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('customer_transactions', customer_id=customer.id)

        if tx_date > timezone.now().date():
            messages.error(request, "Future dates are not allowed.")
            return redirect('customer_transactions', customer_id=customer.id)

        current_balance = customer.get_balance()

        if tx_type in ('due', 'interest'):
            new_balance = current_balance + amount
        else:
            new_balance = current_balance - amount

        # Duplicate check: prevent same transaction within 10 seconds
        last_tx = Transaction.objects.filter(customer=customer).last()
        if last_tx:
            # Check if it was created very recently (within 10 seconds)
            time_diff = (timezone.now() - last_tx.created_at).total_seconds()
            if (time_diff < 10 and
                last_tx.amount == amount and 
                last_tx.type == tx_type and 
                last_tx.date == tx_date and 
                last_tx.reason == reason):
                messages.warning(request, "Duplicate transaction detected and ignored.")
                return redirect('customer_transactions', customer_id=customer.id)

        Transaction.objects.create(
            customer=customer,
            type=tx_type,
            amount=amount,
            date=tx_date,
            reason=reason,
            running_balance=new_balance
        )

        if tx_type == 'due':
            action = "added as DUE"
        elif tx_type == 'interest':
            action = "added as INTEREST"
        else:
            action = "received as PAYMENT"
        messages.success(request, f"₹{amount:.2f} {action}. New balance: ₹{new_balance:.2f}")
        return redirect('customer_transactions', customer_id=customer.id)


class UpdateReasonView(View):
    def post(self, request, pk):
        tx = get_object_or_404(Transaction, pk=pk)
        new_reason = request.POST.get('reason', '')
        tx.reason = new_reason
        tx.save()
        messages.success(request, "Reason updated successfully.")
        return redirect('customer_transactions', customer_id=tx.customer.id)


class DeleteTransactionView(View):
    def post(self, request, pk):
        tx = get_object_or_404(Transaction, pk=pk)
        customer = tx.customer

        # Delete this transaction and all subsequent ones (cascade forward)
        Transaction.objects.filter(
            customer=customer,
            date__gte=tx.date,
            id__gte=tx.id
        ).delete()

        messages.warning(request, "Transaction and all subsequent entries have been deleted.")
        return redirect('customer_transactions', customer_id=customer.id)


class GetBalanceAPIView(View):
    """Simple JSON endpoint to get current balance for JS confirmation dialog."""
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        return JsonResponse({'balance': customer.get_balance()})
