from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from project.Models.Customer import Customer
from project.Forms.Form import CustomerForm,Follow_up,CustomerFollowUpForm
from project.Models.Ticket import Ticket,TicketStatusHistory
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import PermissionDenied


@login_required(login_url='Register:Login')
def Profile(request):
    if request.user.is_staff:
        return redirect('Admin:Dashboard')
 
    customer = Customer.objects.filter(user=request.user).first()
    tickets = Ticket.objects.filter(customer=customer) if customer else []
    follow_ups = customer.follow_ups.all().order_by("Follow_up_date") if customer else []
 
    return render(request, 'Customer/Profile.html', {
        'customer': customer,
        'tickets': tickets,
        'follow_ups': follow_ups,
    })
 
@login_required(login_url='Register:Login')
def Customer_list(request):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    customers = Customer.objects.all()

    q = request.GET.get('q')
    if q:
        customers = customers.filter(
            Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q)
        )

    status = request.GET.get('status')
    if status:
        customers = customers.filter(status=status)

    paginator = Paginator(customers, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'Customer/Customer_list.html', {'customers': page})


@login_required(login_url='Register:Login')
def Customer_create(request):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)

            if not User.objects.filter(username=customer.email).exists():
                new_user = User.objects.create_user(
                    username=customer.email,
                    email=customer.email,
                    password='test@123'   )
                customer.user = new_user

            customer.save()
            return redirect('Customer:Customer_list')
    else:
        form = CustomerForm()
    return render(request, 'Customer/Customer_form.html', {'form': form})


@login_required(login_url='Register:Login')
def Customer_update(request, pk):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('Customer:Customer_list')
    return render(request, 'Customer/Customer_form.html', {'form': form, 'title': 'Edit Customer'})


@login_required(login_url='Register:Login')
def Customer_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('Customer:Customer_list')




def Customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.user.is_staff and not request.user.is_superuser:
        has_access = Ticket.objects.filter(customer=customer, assigned_agent=request.user).exists()
        if not has_access:
            return redirect('Customer:My_customers')

    tickets = Ticket.objects.filter(customer=customer)
    status_history = TicketStatusHistory.objects.filter(
        ticket__customer=customer
    ).select_related('ticket', 'changed_by').order_by('-changed_at')

    return render(request, 'Customer/Customer_detail.html', {
        'customer': customer,
        'tickets': tickets,
        'status_history': status_history,
    })

def My_customers(request):
    if not request.user.is_staff:
        return redirect('Register:Login')

    tickets = Ticket.objects.filter(assigned_agent=request.user)
    customer_ids = tickets.values_list('customer_id', flat=True).distinct()
    customers = Customer.objects.filter(id__in=customer_ids)

    return render(request, 'Customer/My_customers.html', {'customers': customers})


 
def is_staff_user(user):
    return user.is_staff
 
 
# --- Admin / Agent side: full access ---
 
@login_required(login_url='/login/')
@user_passes_test(is_staff_user)
def Followup_list(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
 
    if not request.user.is_staff:
        # Non-staff (customer) can only view their own follow-ups
        if customer.user_id != request.user.id:  # adjust field name if Customer links to User differently
            raise PermissionDenied
 
    follow_ups = customer.follow_ups.all().order_by("Follow_up_date")
    return render(request, "Customer/followup.html", {"customer": customer, "follow_ups": follow_ups})
 
@login_required(login_url='/login/')
@user_passes_test(is_staff_user)
def Followup_save(request, customer_id, followup_id=None):
    customer = get_object_or_404(Customer, pk=customer_id)
    instance = get_object_or_404(Follow_up, pk=followup_id) if followup_id else None

    if request.method == "POST":
        form = CustomerFollowUpForm(request.POST, instance=instance, customer=customer)
        if form.is_valid():
            follow_up = form.save(commit=False)
            follow_up.customer = customer
            follow_up.save()
            return redirect("Customer:Followup_list", customer_id=customer.id)
    else:
        form = CustomerFollowUpForm(instance=instance, customer=customer)
    return render(request, "Customer/followup_form.html", {"form": form, "customer": customer})

 
# --- Customer side: read-only, own record only ---
 
@login_required(login_url='/login/')
def My_followups(request):
    customer = get_object_or_404(Customer, user=request.user)
    follow_ups = customer.follow_ups.all().order_by("Follow_up_date")
    return render(request, "Customer/followup.html", {"customer": customer, "follow_ups": follow_ups})
 