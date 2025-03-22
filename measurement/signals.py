from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Measurement, Result

@receiver(post_save, sender=Measurement)
def create_or_update_results(sender, instance, created, **kwargs):
    """Create or update the results when the measurement is saved"""
    
    #get or create the results
    result, _ = Result.objects.get_or_create(measurement=instance)
    result.save()