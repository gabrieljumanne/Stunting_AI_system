from django.db import models
from core.models import CustomUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dateutil.relativedelta import relativedelta #for precision counting of the age_month

# Create your models here.

#median height and standard deviation logic  functions  

#WHO-BASED DATA - hard corded 

BOYS_HEIGHT_DATA = {0:(49.9, 1.8), 6:(67.6, 2.1), 12:(75.7, 2.3), 24:(87.8, 3.1), 36:(96.1, 3.7), 48:(103.3, 4.1), 60:(108.9, 4.6)}
GIRLS_HEIGHT_DATA = {0:(49.1, 1.9), 6:(65.7, 2.25), 12:(74.1, 2.6), 24:(85.7, 3.2), 36:(95.1, 3.8), 48:(102.7, 4.3), 60:(109.4, 4.7)}

def get_median_height(age_months, gender):
    data = BOYS_HEIGHT_DATA if gender == "M" else GIRLS_HEIGHT_DATA
    ages = sorted(data.keys())

    if age_months in data:
        return  data[age_months][0]
    
    #handling the data edge
    if age_months < ages[0]:
        return data[ages[0]][0]
    if age_months > ages[-1]:
        return data[ages[-1]][0]
    
    # logic fcor not found age in data set 
     
    lower_age = max(a for a in ages if a < age_months)  
    upper_age = min(a for a in ages if a > age_months)
    
    upper_height = data[upper_age][1]
    lower_height = data[lower_age][1]
    
    # linear interpolation 
    ratio = (age_months - lower_age)/(upper_age-lower_age)
    return lower_height + ratio * (upper_height - lower_height)
    
    
def get_sd(age_months, gender):
    data = BOYS_HEIGHT_DATA if gender == "M" else GIRLS_HEIGHT_DATA
    ages = sorted(data.keys())
    
    if age_months in data:
        return data[age_months][1]
    
    #handle the edge ages 
    if age_months < ages[0]:
        return data[ages[0]][1]
    if age_months > ages[-1]:
        return data[ages[-1]][1]
    
    #logic for not found ages 
    
    upper_age = min(a for a in ages if a > age_months)
    lower_age = max(a for a in ages if a < age_months)
    
    upper_std = data[upper_age][1]
    lower_std = data[lower_age][1]
    
    # liner interpolation 
    ratio = (age_months - lower_age)/ (upper_age - lower_age)
    return lower_std  + ratio * (upper_std - lower_std)
    
    
class Child(models.Model):
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
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'role':'parent'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Parent: {self.parent.username})"
    
    
class Measurement(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    height = models.FloatField(_('children height in cm'))
    weight = models.FloatField(_("child weight"), null=True, blank=True)
    age_months = models.IntegerField(_('monthes age for child'), editable=False) #automatically calculated
    date = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        #age_month calculataion logic 
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
        #calculation of HAZ
        median_height = get_median_height(self.measurement.age_months,self.measurement.child.gender)
        sd = get_sd(self.measurement.age_months, self.measurement.child.gender)
        self.haz = (self.measurement.height - median_height) / sd 
        self.is_stunted = self.haz < -2
        if self.is_stunted:
            self.severity = 'Severe' if self.haz < -3 else 'moderate'
            self.recommendation ='Vist our AI-assistance for guidence'
        else:
            self.severity = None
            self.recommendation  = ' You are child is growing well'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.measurement.child.name} ({self.measurement.child.date_of_birth}) - Stunted - {self.is_stunted}"
        
        