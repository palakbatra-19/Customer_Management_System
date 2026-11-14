from django.urls import path
from project.Controller import Admin

app_name = 'Admin'

urlpatterns = [
    path('', Admin.Dashboard, name='Dashboard'),
    path('status-history/', Admin.StatusHistory, name='StatusHistory'),
    path('admin_list/',Admin.Admin_list,name='Admin_list'),

    ]