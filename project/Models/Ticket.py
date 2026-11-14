from django.db import models
from django.contrib.auth.models import User
from project.Models.Customer import Customer


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('billing', 'Billing'),
        ('general', 'General'),
        ('complaint', 'Complaint'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='tickets')
    category=models.CharField(max_length=20,choices=CATEGORY_CHOICES,default='general')
    priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default='medium')
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='open')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_tickets')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=15, choices=Ticket.STATUS_CHOICES, blank=True)
    new_status = models.CharField(max_length=15, choices=Ticket.STATUS_CHOICES)
    description=models.TextField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.ticket.title}: {self.old_status} → {self.new_status}"
    

class TicketActivity(models.Model):
    ACTIVITY_TYPES = [
        ('created', 'Created'),
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('description', 'Description'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.get_activity_type_display()} on {self.ticket.title}"
    

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ticket_comments')
    message = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.ticket.title}"