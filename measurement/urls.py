from django.urls import path 
from . import  views

app_name = 'measurement'

urlpatterns = [
    path('child/register/', views.ChildRegistrationView.as_view(), name='child_register'),
    path('child/<int:child_id>/measure/', views.ChildMeasurementView.as_view(), name="child_measure"),
    path('child/<int:pk>/results/', views.ChildResultsView.as_view(), name="child_results")
]
