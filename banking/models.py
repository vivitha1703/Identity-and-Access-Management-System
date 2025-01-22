from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Customer', 'Customer'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Customer')
    phone_number = models.CharField(max_length=12)

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    failed_attempts = models.IntegerField(default=0)  # Tracks failed login attempts
    is_locked = models.BooleanField(default=False)    # Indicates if the account is locked
    device_id = models.CharField(max_length=255, unique=True, blank=True, null=True)  # New column for device ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'admin_customers'
        
class Transaction(models.Model):
    date = models.DateField()
    time = models.TimeField()
    account_number = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'Credit' or 'Debit'

    class Meta:
        db_table = 'transaction'

    def __str__(self):
        return f"{self.date} {self.time} - {self.customer_name} - {self.amount} ({self.transaction_type})"

class Manager(models.Model):
    LEVEL_CHOICES = [
        ('Junior', 'Junior'),
        ('Middle', 'Middle'),
        ('Senior', 'Senior'),
        ('Top', 'Top'),
    ]
    
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    phone_number = models.CharField(max_length=15)
    years_of_experience = models.IntegerField()
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'manager'

    def __str__(self):
        return f"{self.name} ({self.level})"

class Device(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)  # Link to Customer model
    device_id = models.CharField(max_length=255)  # Unique device identifier
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the device was added

    def __str__(self):
        return f"{self.customer.name} - {self.device_id}"  # Display customer name and device ID