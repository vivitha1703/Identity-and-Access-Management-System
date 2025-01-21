from django.db import models
from banking.models import CustomUser, Customer
import random

# Create your models here.
class Code(models.Model):
    number = models.CharField(max_length=5, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return str(self.number)  # Correctly reference the number field

    def save(self, *args, **kwargs):
        number_list = [x for x in range(10)]  # List of digits 0-9
        code_items = []
        for i in range(5):  # Create a 5-digit code
            num = random.choice(number_list)
            code_items.append(num)
        code_string = "".join(str(item) for item in code_items)
        self.number = code_string  # Assign the generated code to the number field
        super().save(*args, **kwargs)  # Call the parent's save method
