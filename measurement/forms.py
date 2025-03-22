from django import forms 
from .models import Child , Measurement
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

class ChildForm(forms.ModelForm):
    #non-editable input 
    parent = forms.CharField(
        label='Parent',
        disabled=True,
        help_text="You can not change the parent registering this child"
    )
    
    class Meta:
        model = Child
        # parent is excluded in the field displayed and will be set in the view 
        fields = ['name', 'date_of_birth', 'gender']
        #widget for gender and date of birth 
        widgets ={
            'date_of_birth': forms.DateInput(attrs={'type':'date'}),
            'gender': forms.Select()
            
        }
        labels = {
            'name': 'Child\'s Name ', 
            'date_of_birth': 'Date Of Birth',
            'gender':'Gender'
        }
        
        help_text ={
            'date_of_birth': 'Enter child\'s date of birth e.g(YYYY-MM-DD), also years should be atlest above 5 years '
        }
        
    def __init__(self, *args, **kwargs):
        #pop-up the parent value if is available 
        parent_name  = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        
        if parent_name:
            self.fields['parent'].initial = parent_name.username 
            
    def clean_date_of_birth(self):
        #validation of checking the birthdate 
        dob = self.cleaned_data['date_of_birth']
        today = timezone.now().date()
        min_date = today - timedelta(5*365)
        
        if dob >= today:
            raise ValidationError('The date of birth can not be in the future')
        if dob < min_date:
            raise ValidationError('Date of birth must be atlest five years and above ')
        
        return dob
    

class MesurementForm(forms.ModelForm):
    # non-editable child field 
    childname = forms.CharField(
        label= 'Child',
        disabled=True,
        help_text='You can not change the child name'
    )
    
    class Meta:
        model = Measurement
        # child field is excluded and its logic will be set in the view 
        fields = ['height', 'weight']
        
        widgets = {
            'height': forms.NumberInput(attrs={'step':0.1, 'min':30, 'max':200}),
            'weight': forms.NumberInput(attrs={'step':0.1})
            
        }
        
        lables = {
            'height':'Child-height(cm)',
            'weight':'Child-weight(kg)',
        }
        
        help_text = {
            'height':'Enter height in cm , range 30cm -200cm',
            'weight': 'Enter weight in kilogram'
        }
        
    def __init__(self, child, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if child:
            self.fields['childname'].initial = child.name 
            
    def clean_height(self):
        height = self.cleaned_data['height']
        if not(30<=height<=200):
            raise forms.ValidationError("Height must be between 30 and 200")
        
        return height
            
        
