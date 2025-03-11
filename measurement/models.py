from django.db import models
from core.models import CustomUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta #for precision counting of the age_month

# Create your models here.

class Child(models.model):
    GENDER_COICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    
    name = models.CharField(
        _('child name '), 
        max_length=200
    )
    
    date_of_birth = models.DateField(
        _('Date of birth'),
        
    )
    
    gender = models.CharField(
        _('child gender'),
        max_length=1,
        choices=GENDER_COICES
    )
    
    parent = models.ForeignKey(
        _('child parent'), 
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'role':'parent'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Parent: {self.parent.username})"
    
    
class Measurement(models.model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    height = models.FloatField(_('children height in cm'))
    weight = models.FloatField(_("child weight"), null=True, blank=True)
    age_months = models.IntegerField(_('monthes age for child'), editable=False) #automatically calculated
    date = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        #automatically calculating the age_month during saving
        dob = self.child.date_of_birth
        measurement_date = self.date or timezone().now().date()
        delta = relativedelta(measurement_date, dob)
        self.age_months = delta.years * 12 + delta.month
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.child.name} (Height: {self.height} cm - {self.date} )"
    
    class Meta: 
        constraints = [
            models.CheckConstraint(check=models.Q(height__gte=30, height__lte=200), name='height_range')
        ]

class Result(models.Model):
    measurement = models.OneToOneField(Measurement, on_delete=models.CASCADE)
    haz = models.FloatField(_("Height for Age z-score"), editable=False)
    is_stunted = models.BooleanField(_('Is Stunted'), default=False)
    severity = models.CharField(_("Stunting Severity"), max_length=50, null=True, blank=False)
    recommendation = models.TextField()
    
    def save(self, *args, **kwargs):
        pass 