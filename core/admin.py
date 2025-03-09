from django.contrib import admin
from .models import CustomUser, ParentProfile, HealthWorkerProfile

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ParentProfile)
admin.site.register(HealthWorkerProfile)