from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, functions
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Customer
from transactions.models import Transaction
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class AdminDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        search_query = request.GET.get('search', '').strip()
        customers = Customer.objects.filter(user=request.user).order_by(functions.Lower('name'))

        if search_query:
            customers = customers.filter(
                Q(name__icontains=search_query) | Q(phone_number__icontains=search_query)
            )

        customer_data = []
        total_due_all = 0
        customers_with_due = 0

        for customer in customers:
            balance = customer.get_balance()
            customer_data.append({
                'customer': customer,
                'balance': balance,
                'balance_abs': abs(balance)
            })
            if balance > 0:
                total_due_all += balance
                customers_with_due += 1

        context = {
            'customers': customer_data,
            'total_due_all': total_due_all,
            'customers_with_due': customers_with_due,
            'total_customers': customers.count(),
            'search_query': search_query,
        }
        return render(request, 'customers/dashboard.html', context)


class CustomerRegisterView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not name or not phone:
            messages.error(request, "Name and Phone number are required.")
            return redirect('dashboard')

        if Customer.objects.filter(user=request.user, phone_number=phone).exists():
            messages.error(request, "A customer with this phone number already exists.")
        else:
            Customer.objects.create(
                user=request.user,
                name=name,
                phone_number=phone,
                email=email if email else None,
                address=address if address else None
            )
            messages.success(request, f"Customer '{name}' added successfully!")

        return redirect('dashboard')


class CustomerTransactionView(View):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)

        # Auth: business owner OR customer logged in via session
        is_admin = request.user.is_authenticated and customer.user == request.user
        is_logged_customer = request.session.get('customer_id') == customer.id

        if not (is_admin or is_logged_customer):
            return redirect('customer_login')

        transactions = customer.transactions.all().order_by('date', 'id')
        total_due = customer.get_balance()

        context = {
            'customer': customer,
            'transactions': transactions,
            'total_due': total_due,
            'total_due_abs': abs(total_due),
            'is_admin': is_admin,
            'today': timezone.now().date(),
        }
        return render(request, 'customers/transactions.html', context)


class CustomerLoginView(View):
    def get(self, request):
        return render(request, 'customers/customer_login.html')

    def post(self, request):
        phone = request.POST.get('phone', '').strip()
        try:
            customer = Customer.objects.get(phone_number=phone)
            request.session['customer_id'] = customer.id
            messages.success(request, f"Logged in as {customer.name}")
            return redirect('customer_transactions', customer_id=customer.id)
        except Customer.DoesNotExist:
            messages.error(request, "No customer found with this phone number.")
            return redirect('customer_login')
        except Customer.MultipleObjectsReturned:
            # If multiple businesses have a customer with the same phone
            customer = Customer.objects.filter(phone_number=phone).first()
            request.session['customer_id'] = customer.id
            messages.success(request, f"Logged in as {customer.name}")
            return redirect('customer_transactions', customer_id=customer.id)


class GeneratePDFView(View):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)

        # Auth check
        is_admin = request.user.is_authenticated and customer.user == request.user
        is_logged_customer = request.session.get('customer_id') == customer.id

        if not (is_admin or is_logged_customer):
            return redirect('customer_login')

        # Create a file-like buffer to receive PDF data
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Add Header
        elements.append(Paragraph(f"<b>Business: {customer.user.business_name}</b>", normal_style))
        elements.append(Paragraph(f"<b>Customer Ledger: {customer.name}</b>", title_style))
        elements.append(Paragraph(f"Phone: {customer.phone_number}", normal_style))
        if customer.email:
            elements.append(Paragraph(f"Email: {customer.email}", normal_style))
        elements.append(Spacer(1, 12))

        # Add Table
        data = [['Date', 'Type', 'Reason', 'Amount', 'Balance']]
        transactions = customer.transactions.all().order_by('date', 'id')
        
        for tx in transactions:
            data.append([
                tx.date.strftime('%d/%m/%Y'),
                tx.get_type_display(),
                tx.reason if tx.reason else '-',
                f"Rs. {tx.amount:.2f}",
                f"Rs. {tx.running_balance:.2f}"
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        # Add Total Due
        total_due = customer.get_balance()
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>Total Due Amount: Rs. {total_due:.2f}</b>", styles['Heading3']))

        # Build PDF
        doc.build(elements)

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{customer.name}_ledger.pdf"'
        return response
