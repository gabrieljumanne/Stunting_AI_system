from django import forms 
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ParentProfile, HealthWorkerProfile

#parent registration form 

class ParentRegistrationForm(UserCreationForm):
    address = forms.CharField(
        widget=forms.Textarea, 
        help_text=_("Enter your residential address.")
    )
    
    phone_number = forms.CharField(
        max_length=10,
        help_text=_("Enter your phone number (digit only).")
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'fullname', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #pre-set and hide  the role field
        self.fields['role'] = forms.CharField(initial='parent',widget=forms.HiddenInput() )
    
    def clean_email(self):
        if email := self.cleaned_data.get('email'):
            if CustomUser.objects.filter(email=email):
                raise ValidationError(_("This email is already in use. "))
            
            if email.endswith('@forbidden-domain.com'):
               raise ValidationError(_("This email domain is not allowed"))
           
            if email.endswith('@spam.com'):
               raise ValidationError(_("This email provider is not allowed"))
           
            return email 
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError(_("Phone number must contain only digits."))
        
        return phone_number
    
    def clean(self):
        """performing cross validation"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        
        if email and username and username.lower() in email.lower():
            raise ValidationError(_("Username should not be part of the email"))
        
        return cleaned_data
    
    # linking to parent profile after saving
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'parent'
        if commit:
            user.save()
            ParentProfile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user
    
# Health worker registration form 

class HealthWorkerRegistrationForm(UserCreationForm):
    professional_id = forms.CharField(
        max_length= 50 ,
        help_text=_("Enter your professinal ID. ")
    )
    
    health_facility = forms.CharField(
        widget=forms.Textarea,
        max_length=100,
        help_text=_("Enter Your Health Facility name")
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'fullname', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #pre-set the health_worker role value
        self.fields['role']= forms.CharField(initial='health_worker', widget=forms.HiddenInput)
        
    def clean_email(self):
        if email := self.cleaned_data.get('email'):
            if CustomUser.objects.filter(email=email):
                raise ValidationError(_("This email is already in use. "))
            
            if email.endswith('@forbidden-domain.com'):
               raise ValidationError(_("This email domain is not allowed"))
           
            if email.endswith('@spam.com'):
               raise ValidationError(_("This email provider is not allowed"))
           
            return email 
    
    def clean_professional_id(self):
        professional_id = self.cleaned_data.get('professional_id')  
        if HealthWorkerProfile.objects.filter(professional_id=professional_id).exists():
            raise ValidationError(_("This professinal ID is already in use"))  
        
        return professional_id
    
    def clean(self):
        """performing cross validation"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        
        if email and username and username.lower() in email.lower():
            raise ValidationError(_("Username should not be part of email.")) 
        
        return cleaned_data
    
    #linking to Healthworker profile after saving
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'health_worker'
        if commit:
            user.save()
            HealthWorkerProfile.objects.create(
                user=user,
                professional_id=self.cleaned_data['professional_id'],
                health_facility=self.cleaned_data['health_facility']
            )
            
        return user
    
    
class CustomAuthenticationForm(AuthenticationForm):
    # remember me field 
    remember_me = forms.BooleanField(required=False, initial=False, label=_("Remember me"))
    
    def clean(self):
        #parent clean methon to handle username/password validation
       
        return super().clean()
           

class BaseProfileEditForm(forms.ModelForm):
    #read-only field for role and username 
    username_display = forms.CharField(required=False, label="Username", widget=forms.TextInput(attrs={'readonly':True}))
    role_display = forms.CharField(required=False, label="Role", widget=forms.TextInput(attrs={'readonly': True}))
    
    class Meta:
        model = CustomUser
        #only editable fields .
        fields = ['fullname', 'email', 'language_preferences']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #intialization of the non-editable fields 
        if self.instance.pk:
            self.fields['username_display'].initial = self.instance.username 
            self.fields['role_display'].initial = self.instance.role
            
                
# parentedit form 
class ParentprofileEditForm(BaseProfileEditForm):
    """Form for parent-specific fields"""
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    phone_number = forms.CharField(max_length=10, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize profile fields if profile exists
        try:
            if self.instance and self.instance.pk:
                parent_profile = ParentProfile.objects.get(user=self.instance)
                self.fields['address'].initial = parent_profile.address
                self.fields['phone_number'].initial = parent_profile.phone_number
        except ParentProfile.DoesNotExist:
            pass
            
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Get or create the profile model
            parent_profile, created = ParentProfile.objects.get_or_create(user=user)
            parent_profile.address = self.cleaned_data['address']
            parent_profile.phone_number = self.cleaned_data['phone_number']
            parent_profile.save()
        return user      
        
        
class HealthWorkerProfileEditForm(BaseProfileEditForm):
    """form for Health worker specific fields """
    professional_id= forms.CharField(max_length=50, required=False)
    health_facility = forms.CharField(max_length=50, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #initialization of profiles fields 
        try:
            if self.instance and self.instance.pk:
                hw_profile = HealthWorkerProfile.objects.get(user=self.instance)
                self.fields['professinal_id'].initial = hw_profile.professional_id
                self.fields['health_facility'].initial = hw_profile.health_facility
        except HealthWorkerProfile.DoesNotExist:
            pass
        
    def save(self, commit=True):
        user = super().save(commit=commit)
        hw_profile, created = HealthWorkerProfile.objects.get_or_create(user=user)
        hw_profile.professional_id = self.cleaned_data['professional_id']
        hw_profile.health_facility = self.cleaned_data['health_facility']
        hw_profile.save()
        return user