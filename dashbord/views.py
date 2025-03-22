from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from measurement.models import Child, Measurement, Result
from django.utils import timezone
from datetime import timedelta, date 


#parent Dashbord 

class ParentDashbord(LoginRequiredMixin, TemplateView):
    template_name = 'dashbord/parent.html'
    
    #configuring the context data 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['childreen'] = Child.objects.filter(parent=self.request.user)
        latest_child = Child.objects.filter(parent=self.request.user).order_by('-id').first()
        context['latest_child']= latest_child
        
        # latest results for this recently added child by this parent
        if latest_child:
            if latest_measurement := Measurement.objects.filter(child=latest_child).order_by('-date').first():
                latest_child_result = Result.objects.filter(measurement=latest_measurement).first()
                context['latest_child_results'] = latest_child_result
        
        #context for latest articles (5)
        
        return context 
    
    
class HealthWorkerDarshbord(LoginRequiredMixin, TemplateView):
    template_name = 'dashbord/health_worker.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'health_worker':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #overall statics of data 
        context['total_childreen'] = Child.objects.count()
        context['total_measurements'] = Measurement.objects.count()
        context['stunted_childreens'] = Result.objects.filter(is_stunted=True).values('measurement__child').distinct().count()
        
        
        # recent measurement for all accross childreen (only Ten.)
        context['recent_measurement'] = Measurement.objects.all().order_by('-date')[:10]
        
        #Age group statictics for child 
        
        from django.db.models import Count, Case, When, IntegerField
        age_stats = Child.objects.annotate(
            age_group=Case(
            When(date_of_birth__lt=date.today() - timedelta(days=365*5), then=3),  # >5 years
            When(date_of_birth__lt=date.today() - timedelta(days=365*2), then=2),  # 2-5 years
            When(date_of_birth__lt=date.today() - timedelta(days=365), then=1),    # 1-2 years
            default=0,  # <1 year
            output_field=IntegerField(),
            )
        ).values('age_group').annotate(count=Count('id'))
        
        context['age_stats'] = age_stats