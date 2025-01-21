from banking.models import CustomUser
from .models import Code
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def post_save_generate_code(sender, instance, created, *args, **kwargs):
    if created:
        code_instance = Code.objects.create(user=instance)
        print(code_instance.number)
        # logger.info(f'Code created for user {instance.username}: {code_instance.number}')

