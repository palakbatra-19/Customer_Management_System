from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from project.Models.Customer import Customer
from project.Models.Ticket import Ticket, TicketStatusHistory
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import json



@login_required(login_url='Register:Login')
def Dashboard(request):
    if not request.user.is_superuser:
        if request.user.is_staff:
            return redirect('Ticket:Ticket_list')
        return redirect('Customer:Profile')

    admin_tickets = Ticket.objects.filter(assigned_agent__is_superuser=True).count()
    agent_tickets = Ticket.objects.filter(assigned_agent__is_staff=True, assigned_agent__is_superuser=False).count()
    customer_tickets = Ticket.objects.filter(assigned_agent__isnull=True).count()

    role_labels = ['Admin', 'Agent', 'Unassigned']
    role_ticket_counts = [admin_tickets, agent_tickets, customer_tickets]

    # NEW: tickets grouped by the customer who created them
    tickets_per_customer = (
        Ticket.objects.values('customer__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    customer_ticket_labels = [c['customer__name'] or 'Unknown' for c in tickets_per_customer]
    customer_ticket_counts = [c['count'] for c in tickets_per_customer]

    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    closed_tickets = Ticket.objects.filter(status='closed').count()
    active_customers = Customer.objects.filter(status='active').count()
    inactive_customers = Customer.objects.filter(status='inactive').count()

    # Generate charts
    ticket_chart = make_pie(
        ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed'],
        [open_tickets, in_progress_tickets, pending_tickets, resolved_tickets, closed_tickets],
        ['#3498db', '#f39c12', '#9b59b6', '#27ae60', '#7f8c8d']
    )
    customer_chart = make_pie(
        ['Active',  'Inactive'],
        [active_customers, inactive_customers],
        ['#11998e', '#e67e22']
    )
    
    total_customers_count = Customer.objects.count()

    combined_labels = ['Admin', 'Agent', 'Customers']
    combined_counts = [admin_tickets, agent_tickets, total_customers_count]
    agent_chart = make_pie(
    combined_labels,
    combined_counts,
    ['#6a3fd0', '#14affc', '#6ff029']
)


    context = {
        'total_customers': Customer.objects.count(),
        'total_tickets': Ticket.objects.count(),
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'pending_tickets': pending_tickets,
        'closed_tickets': closed_tickets,

        'customers': Customer.objects.all().order_by('-created_at'),
        'tickets': Ticket.objects.all().order_by('-created_at'),
        'users': User.objects.all().order_by('username'),
        'status_history': TicketStatusHistory.objects.select_related('ticket', 'changed_by').order_by('-changed_at')[:20],

        'active_customers': active_customers,
        'inactive_customers': inactive_customers,

        
        'ticket_chart': ticket_chart,
        'customer_chart': customer_chart,
        'agent_chart': agent_chart,
    }
    return render(request, 'Admin/Dashboard.html', context)


@login_required(login_url='Register:Login')
def StatusHistory(request):
    if request.user.is_superuser:
        history = TicketStatusHistory.objects.all()
    elif request.user.is_staff:
        history = TicketStatusHistory.objects.filter(ticket__assigned_agent=request.user)
    else:
        return redirect('Ticket:Ticket_list')

    return render(request, 'Admin/StatusHistory.html', {'history': history.order_by('-changed_at')})



def make_pie(labels, values, colors):
    labels = [f'{l} ({v})' for l, v in zip(labels, values)]

    plt.figure(figsize=(4, 4.5))
    plt.pie(values, colors=colors, autopct='%1.0f%%', pctdistance=1.15)
    plt.legend(labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=9)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()




@login_required(login_url='Register:Login')
def Admin_list(request):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    admin = User.objects.filter(is_superuser=True)
    return render(request, 'Admin/Admin_list.html', {'admin': admin})