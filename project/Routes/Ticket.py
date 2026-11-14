from django.urls import path
from project.Controller import Ticket

app_name = 'Ticket'

urlpatterns = [
    path('', Ticket.Ticket_list, name='Ticket_list'),
    path('new/', Ticket.Ticket_create, name='Ticket_create'),
    path('<int:pk>/edit/', Ticket.Ticket_update, name='Ticket_update'),
    path('<int:pk>/delete/', Ticket.Ticket_delete, name='Ticket_delete'),
    path('<int:pk>/detail/', Ticket.Ticket_detail, name='Ticket_detail'),
]