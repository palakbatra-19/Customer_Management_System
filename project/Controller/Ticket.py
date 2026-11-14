from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from project.Models.Customer import Customer,Follow_up
from project.Models.Ticket import Ticket
from project.Forms.TicketForm import TicketForm,StatusChangeForm
from project.Validators import validate_status_transition
from project.Models.Ticket import Ticket, TicketStatusHistory
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from project.Models.Ticket import Ticket, TicketStatusHistory, TicketActivity, TicketComment
from project.Forms.TicketForm import TicketForm, StatusChangeForm, TicketCommentForm, TicketReplyForm




def log_activity(ticket, activity_type, user, old_value=None, new_value=None, description=''):
    TicketActivity.objects.create(
        ticket=ticket,
        activity_type=activity_type,
        old_value=old_value,
        new_value=new_value,
        description=description,
        changed_by=user,
    )
@login_required(login_url='Register:Login')
def Ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)

            if not request.user.is_staff and not request.user.is_superuser:
                customer = Customer.objects.filter(user=request.user).first()
                ticket.customer = customer
                ticket.priority = 'medium'
                ticket.status = 'open'
                ticket.assigned_agent = None

            ticket.save()
            log_activity(ticket, 'created', request.user, description=f'Ticket "{ticket.title}" created')
            return redirect('Ticket:Ticket_list')
    else:
        form = TicketForm(user=request.user)

    return render(request, 'Ticket/Ticket_form.html', {'form': form, 'title': 'New Ticket'})




@login_required(login_url='Register:Login')
def Ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    is_owner = not request.user.is_staff and ticket.customer.user == request.user
    is_agent = request.user.is_staff and not request.user.is_superuser and ticket.assigned_agent == request.user
    is_admin = request.user.is_superuser

    if not (is_owner or is_agent or is_admin):
        messages.error(request, "You don't have permission to edit this ticket.")
        return redirect('Ticket:Ticket_list')

    old_status = ticket.status
    old_agent = ticket.assigned_agent
    form = TicketForm(request.POST or None, instance=ticket, user=request.user)

    if form.is_valid():
        new_status = form.cleaned_data.get('status', old_status)

        if is_agent:
            try:
                validate_status_transition(old_status, new_status)
            except ValidationError as e:
                form.add_error('status', e.message)
                return render(request, 'Ticket/Ticket_form.html', {'form': form, 'title': 'Edit Ticket'})

        updated_ticket = form.save()
        if old_status != updated_ticket.status:
            TicketStatusHistory.objects.create(
                ticket=updated_ticket,
                old_status=old_status,
                new_status=updated_ticket.status,
                description=form.cleaned_data.get('description', ''),
                changed_by=request.user
            )
        
        
            log_activity(updated_ticket, 'status_change', request.user,
                         old_value=old_status, new_value=updated_ticket.status)

        new_agent = updated_ticket.assigned_agent
        if old_agent != new_agent:
            log_activity(updated_ticket, 'assignment', request.user,
                         old_value=old_agent.username if old_agent else 'Unassigned',
                         new_value=new_agent.username if new_agent else 'Unassigned')

        return redirect('Ticket:Ticket_list')
    return render(request, 'Ticket/Ticket_form.html', {'form': form, 'title': 'Edit Ticket'})



@login_required(login_url='Register:Login')
def Ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    status_history = ticket.status_history.order_by('-changed_at')
    activities = ticket.activities.order_by('-changed_at')

    agents = User.objects.filter(is_staff=True, is_superuser=False)
    is_staff_member = request.user.is_staff or request.user.is_superuser

    if request.method == 'POST':
        if 'assign_agent' in request.POST:
            if request.user.is_superuser:
                agent_id = request.POST.get('agent_id')
                old_agent = ticket.assigned_agent
                new_agent = User.objects.filter(pk=agent_id).first() if agent_id else None
                ticket.assigned_agent = new_agent
                ticket.save()
                log_activity(ticket, 'assignment', request.user,
                            old_value=old_agent.username if old_agent else 'Unassigned',
                            new_value=new_agent.username if new_agent else 'Unassigned')
            return redirect('Ticket:Ticket_detail', pk=ticket.pk)

        if 'add_comment' in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                log_activity(ticket, 'comment', request.user,
                            description=comment_form.cleaned_data['comment'])
            return redirect('Ticket:Ticket_detail', pk=ticket.pk)

        if 'add_team_comment' in request.POST:
            if not is_staff_member:
                messages.error(request, "You don't have permission to post here.")
                return redirect('Ticket:Ticket_detail', pk=ticket.pk)
            reply_form = TicketReplyForm(request.POST)
            if reply_form.is_valid():
                team_comment = reply_form.save(commit=False)
                team_comment.ticket = ticket
                team_comment.author = request.user
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    team_comment.parent_id = parent_id
                team_comment.save()
            return redirect('Ticket:Ticket_detail', pk=ticket.pk)

        form = StatusChangeForm(request.POST)
        if form.is_valid():
            old_status = ticket.status
            new_status = form.cleaned_data['new_status']
            description = form.cleaned_data['description']

            TicketStatusHistory.objects.create(
                ticket=ticket,
                old_status=old_status,
                new_status=new_status,
                description=description,
                changed_by=request.user,
            )
            log_activity(ticket, 'status_change', request.user,
                        old_value=old_status, new_value=new_status, description=description)

            ticket.status = new_status
            ticket.save()

            return redirect('Ticket:Ticket_detail', pk=ticket.pk)
    else:
        form = StatusChangeForm(initial={'new_status': ticket.status})

    comment_form = TicketCommentForm()
    reply_form = TicketReplyForm()
    team_comments = ticket.comments.filter(parent__isnull=True).prefetch_related('replies') if is_staff_member else None

    return render(request, 'Ticket/Ticket_detail.html', {
        'ticket': ticket,
        'status_history': status_history,
        'activities': activities,
        'form': form,
        'comment_form': comment_form,
        'agents': agents,
        'is_staff_member': is_staff_member,
        'team_comments': team_comments,
        'reply_form': reply_form,
    })


@login_required(login_url='Register:Login')
def Ticket_list(request):
    if request.user.is_superuser:
        tickets = Ticket.objects.all()
    elif request.user.is_staff:
        tickets = Ticket.objects.filter(assigned_agent=request.user)
    else:
        customer = Customer.objects.filter(user=request.user).first()
        tickets = Ticket.objects.filter(customer=customer)

    search_query = request.GET.get('q')
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    tickets = tickets.order_by('customer','-created_at')

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Ticket/Ticket_list.html', {
        'page_obj': page_obj,
        'search_query': search_query or '',
        'status_filter': status_filter or '',
    })


@login_required(login_url='Register:Login')
def Ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    is_owner = not request.user.is_staff and ticket.customer.user == request.user
    is_admin = request.user.is_superuser

    if not (is_owner or is_admin):
        messages.error(request, "You don't have permission to delete this ticket.")
        return redirect('Ticket:Ticket_list')

    if request.method == 'POST':
        ticket_title = ticket.title
        ticket.delete()
        messages.success(request, f'Ticket "{ticket_title}" deleted successfully.')
        return redirect('Ticket:Ticket_list')

    return render(request, 'Ticket/Ticket_confirm_delete.html', {'ticket': ticket})




@login_required(login_url='Register:Login')
def TicketListPage(request):
    tickets = Ticket.objects.filter(user=request.user) if not request.user.is_staff else Ticket.objects.all()
    return render(request, "Ticket/TicketList.html", {"tickets": tickets})