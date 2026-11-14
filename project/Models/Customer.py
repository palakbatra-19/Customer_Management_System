from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Customer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, blank=True)
    company = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lead')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Follow_up(models.Model):
    STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
        ]
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="follow_ups")
    ticket = models.ForeignKey("Ticket", on_delete=models.SET_NULL,null=True,blank=True,related_name="follow_ups",)
    Follow_up_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
 
    def __str__(self):
        return f"{self.customer} - {self.Follow_up_date:%Y-%m-%d}"