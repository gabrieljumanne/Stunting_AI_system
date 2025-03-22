from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator
from django.core.exceptions import ValidationError


# Custom usermanager
class CustomUsermanager(BaseUserManager):
    def create_user(self, username, email, fullname,role, password=None, **extra_fields):
        """create and return regular user wih required fields"""
        if not username:
            raise ValueError("User must have the username")
        if not email:
            raise ValueError("user must have an email address")
        if not fullname:
            raise ValueError("User must have a fullname")
        if role not in ['parent', 'health_worker']:
            raise ValueError("Role must me either 'parent' or 'health_worker' ")
        
        email = self.normalize_email(email)
        #user-creation and password set
        user = self.model(
            username=username,
            email=email,
            fullname=fullname,
            role = role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, fullname, password=None, **extra_fields):
        """create and return super user"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)     
        
        # super user is the health_worker
        return self.create_user(
            username=username,
            email=email,
            fullname=fullname,
            role='health_worker',
            password=password,
            **extra_fields
        )   
        
    def get_by_natural_key(self, username):
        """Required for the django authentication """
        return self.get(username=username)
        



#user model(profile)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        unique= True,
        help_text=_("email must be unique")
    )
    
    username = models.CharField(
        _("User_name"),
        max_length=50,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_]+$',
            message=_("Username must be alphanumeric or should contain underscore")
        )]
    )
    
    fullname = models.CharField(
    _("user full name"),
    max_length=250,
    unique=False,
    help_text=_('Enter your full name as appeared on your official document')
    )
    
    ROLE_CHOICE = (
        ('parent', 'Parent'),
        ('health_worker', 'Health Worker')
    )
    
    role = models.CharField(
        _("user role"),
        max_length= 20,
        choices=ROLE_CHOICE
    )
    
    # account management field
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user account should be treated as active")
    )
    
    is_staff = models.BooleanField(
        _('staff'),
        default=False,
        help_text=_("Designates whether this user account should be treated as staff")
    )
    
    deleated_at = models.DateTimeField(
        _("deleated at"),
        null= True,
        blank=True,
        help_text=_("Time stamp for the soft deletion")
    )
    
    # tracking fields 
    date_joined = models.DateTimeField(
        _("date joined"), 
        default=timezone.now
    )
    
    # account preference
    language_preferences = models.CharField(
        _("language preference"),
        max_length=20,
        choices=[
            ('eng', _("English")),
            ('swa', _("swahili")),
            ('fr', _('French')),
        ],
        default='eng',

    )
    #usermanager
    objects = CustomUsermanager()
    # model configuration
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [
        "email",
        "fullname",
        "role",
    ]
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ["-date_joined"]
        
    def __str__(self):
        return self.email
    
    def get_fullname(self):
        return self.fullname
    
    def get_short_name(self):
        return self.username
    
    def set_language_preference(self, language):
        """
        Updates the user's language preference.
        """
        if language in ["eng", "swa", "fr"]:
            self.language_preferences = language
            self.save(update_fields=["language_preferences"])

    def soft_delete(self):
        """soft delete the user account"""
        self.deleated_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleated_at", "is_active"])
        

# Role-based profile

class ParentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    address = models.TextField(
        _("parent address"),
        max_length=100,
    )
    
    phone_number = models.CharField(
        _("phone number"),
        max_length= 10
    )
    
    def __str__(self):
        return self.user
    
    class Meta:
        verbose_name = _("Parent Profile")
 
   
class HealthWorkerProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )
    
    professional_id = models.CharField(
        _("Professional_id"),
        max_length= 50
    )
    
    health_facility = models.CharField(
        _("Health facility"),
        max_length= 100
    )
    
    def __str__(self):
        return self.user
    
    class Meta:
        verbose_name = _("Health worker Profile")