from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import CustomUser, ParentProfile, HealthWorkerProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'parent':
           ParentProfile.objects.create(user=instance) 
        elif instance.role == 'health_worker':
            HealthWorkerProfile.objects.create(user=instance)