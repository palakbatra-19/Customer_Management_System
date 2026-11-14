from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from project.Forms.Agentform import AgentForm
from project.Models.Ticket import Ticket, TicketStatusHistory


# def Agent_list(request):
#     agents = User.objects.filter(is_staff=True)
#     return render(request, 'Agent/Agent_list.html', {'agents': agents})

def Agent_detail(request, pk):
    agents = get_object_or_404(Agent_list, pk=pk)
    tickets = Ticket.objects.filter(agents=agents)
    return render(request, 'Agent/Agent_detail.html', {
        'agents': agents,
        'tickets': tickets,
    })

@login_required(login_url='Register:Login')
def Agent_list(request):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')
    agents = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)
    
    return render(request, 'Agent/Agent_list.html', {'agents': agents})

@login_required(login_url='Register:Login')
def Agent_create(request):
    if not request.user.is_superuser:
        return redirect('Ticket:Ticket_list')

    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Agent:Agent_list')
    else:
        form = AgentForm()

    return render(request, 'Agent/Agent_form.html', {'form': form, 'title': 'New Agent'})