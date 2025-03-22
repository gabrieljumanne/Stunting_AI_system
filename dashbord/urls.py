from django.urls import path
from .views import ParentDashbord, HealthWorkerDarshbord

app_name = "dashbord"

urlpatterns = [
    path('parent/', ParentDashbord.as_view(), name='parent_dashbord'),
    path('health-worker/',HealthWorkerDarshbord.as_view(), name='healt-worker-dashbord')
]
