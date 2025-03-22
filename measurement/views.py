from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from .forms import ChildForm, MesurementForm
from .models import Child, Measurement, Result


# ChildregistrationView

class ChildRegistrationView(CreateView):
    model = Child
    form_class = ChildForm
    template_name = 'measurement/child_register.html'
    success_url = reverse_lazy('measurement:child_measure')
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        #check if the user as the parent role 
        if request.user.role != 'parent':
            messages.error(request, "Only parents can register childreen")
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)
    
    #passing the parent value manually to form constructor kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['parent'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """set the parent field to the login user"""
        form.instance.parent = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Child {form.instance.name} registered succesffuly. ")
        
        return response
        
    def form_invalid(self, form):
        messages.error(self.request, "Please correct all errors below")
        return super().form_invalid(form)
        

#child-measurementView

class ChildMeasurementView(CreateView):
    model = Measurement
    form_class = MesurementForm
    template_name = 'measurement/child_measure.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verify the user is the parent of the child """
        child_id = self.kwargs['child_id']
        if not Child.objects.filter(
            id=child_id,
            parent=request.user
        ).exists():
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)
    
    #success url
    def get_success_url(self):
        return reverse_lazy('measurement:child_results', kwargs={'pk': self.kwargs['child_id']})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #get child and pass to the form 
        self.child = get_object_or_404(
            Child, 
            pk = self.kwargs['child_id'],
            parent = self.request.user
        )
        kwargs['child'] = self.child
        return kwargs
    
    def form_valid(self, form):
        """set the child relationship in Measurement instance before saving"""
        form.instance.child = self.child 
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the below errors")
        return super().form_invalid(form)
        
        
    def get_context_data(self, **kwargs):
        """pass the child to the template context"""
        context = super().get_context_data(**kwargs)
        context['child'] = self.child
        
        return context
    

# child - results view 

class ChildResultsView(DetailView):
    model = Result
    template_name = 'measurement/child_results.html'
    context_object_name = 'result'
    
    def get_object(self, queryset=None):
        """Get the most recent child results for specfic childreen"""
        #get ID from the url parameter
        
        child_id = self.kwargs['pk']
        
        #get recent result from specific child 
        
        return get_object_or_404(
            Result,
            measurement__child__id = child_id,
            measurement__child__parent = self.request.user,
        )
        