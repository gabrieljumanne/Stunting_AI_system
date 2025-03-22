from django.urls import path
from .views import UserLogInView, UserLogOutView, ParentRegistrationView, HealthWorkerRegistrationView, UserRegistrationView

app_name = "core"

urlpatterns = [
    path('', UserRegistrationView.as_view(),name='register' ),# as the landing page 
    path('register/parent/', ParentRegistrationView.as_view(),name='parent_registration' ),
    path('register/heath-worker/', HealthWorkerRegistrationView.as_view(),name='health_worker_registration' ),
    path('login/', UserLogInView.as_view(),name='login' ),
    path('logout/', UserLogOutView.as_view(),name='logout' )
]