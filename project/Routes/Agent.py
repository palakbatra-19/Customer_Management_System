from django.urls import path
from project.Controller import Agent

app_name = 'Agent'

urlpatterns = [
    
    path('', Agent.Agent_list, name='Agent_list'),
    path('<int:pk>/detail/',Agent.Agent_detail, name='Agent_detail'),
    path('agent/new/', Agent.Agent_create, name='Agent_create'),
   
    
    ]