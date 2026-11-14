from django.urls import path
from project.Controller import Customer

app_name = 'Customer'

urlpatterns = [
    path('', Customer.Customer_list, name='Customer_list'),
    path('new/', Customer.Customer_create, name='Customer_create'),
    path('<int:pk>/edit/', Customer.Customer_update, name='Customer_update'),
    path('<int:pk>/delete/', Customer.Customer_delete, name='Customer_delete'),
    path('me/', Customer.Profile, name='Profile'),
    path('<int:pk>/detail/',Customer.Customer_detail, name='Customer_detail'),
    path('mycustomers/', Customer.My_customers, name='My_customers'),
    path("<int:customer_id>/follow-ups/<int:followup_id>/edit/", Customer.Followup_save, name="Followup_edit"),
    
    path("<int:customer_id>/follow-ups/", Customer.Followup_list, name="Followup_list"),
    path("<int:customer_id>/follow-ups/new/", Customer.Followup_save, name="Followup_create"),
   
]
