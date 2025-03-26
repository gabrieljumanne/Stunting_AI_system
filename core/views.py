from django.shortcuts import render, redirect
from django.conf import settings 
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.views.generic.edit import CreateView 
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from .forms import ParentRegistrationForm, HealthWorkerRegistrationForm, CustomAuthenticationForm, ParentprofileEditForm, HealthWorkerProfileEditForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CustomUser
from django.http import JsonResponse

# Create your views here.

class  UserRegistrationView(TemplateView):
    """fall back pazge for non authenticated user"""
    template_name = 'core/register.html'
     
               
    

@method_decorator(sensitive_post_parameters(), name='post')
class ParentRegistrationView(CreateView):
    form_class = ParentRegistrationForm
    template_name = 'core/parent_register.html'
    success_url = reverse_lazy('core:login')
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        #redirect login users to home page 
        # if request.user.is_authenticated:
        #     messages.info(request, "You are ready registed and login")
        #     if request.user.role == 'parent':
        #         return redirect(reverse_lazy('dashbord:parent_dashbord'))
        #     else:
        #         return redirect(reverse_lazy('dashbord:healt-worker-dashbord'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Dear Parent,  registraion Succefull!")
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct above errors ! "
        )
        return super().form_invalid(form)

@method_decorator(sensitive_post_parameters(), name='post')
class HealthWorkerRegistrationView(CreateView):
    form_class = HealthWorkerRegistrationForm
    template_name = 'core/health_worker_register.html'
    success_url = reverse_lazy('core:login')
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        #redirect login and registered user to home page 
        if request.user.is_authenticated():
            messages.info(request, "You are already registered and login")
            return redirect(reverse_lazy('core:home'))
        
        return super().dispatch(request, *args, **kwargs)
    
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Dear Healthworker, Registration Successfully")
        
        return response
    
    def form_invalid(self, form): 
        response = super().form_invalid(form)
        messages.error(
            self.request, 
            "Please correct the above errors "
        )
        
class UserLogInView(LoginView):
    template_name = 'core/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    #security decorators 
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    @method_decorator(sensitive_variables('password'))
    def dispatch(self, request, *args, **kwargs):
        #check if the user is already login and redirects if .
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL  point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        
        if request.is_secure() and not settings.DEBUG:
            #checking the safe of redirected url 
            # works in production mode 
            # Ensure the URL is allowed
            next_url = request.POST.get('next', request.GET.get('next'))
            if next_url and not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                raise PermissionDenied(_("Invalid redirect URL"))
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """Redirect users based on their role after login."""
        if self.request.user.role == 'parent':
            return reverse_lazy('dashbord:parent_dashbord')
        elif self.request.user.role == 'health_worker':
            return reverse_lazy('dashbord:health_worker_dashbord')
        return reverse_lazy('core:home')
    

class UserLogOutView(LogoutView):
    next_page = reverse_lazy("core:register")
    
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        
        if request.method != 'POST': 
            messages.warning(
                self.request, 
                _("Please can use the logout button to logout")
            )
            return redirect(reverse_lazy("core:register"))
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """processing the logout(session cleaning) and redirect the user mechanism"""
        
        # get the username 
        username = request.user.get_short_name() or request.user.username
        
        #cleaning the session sensitive data 
        for key in list(request.session.keys()):
            if key.startswith('sensitive_'):
                del request.session[key]
        
        # logout the user
        response = super().post(request, *args, **kwargs)

        messages.success(
            self.request, 
            _(f"Goodbye, {username}! , You are successfully logged out")
        )
        
        # clear all session data 
        request.session.flush()
        
        return response 
    
    def get_next_page(self):
        """Returns the url of the nextpage to redirect after the logout
        """
        next_page = self.request.POST.get('next') or self.request.GET.get('next')
        
        # validity check for the next page 
        if next_page and url_has_allowed_host_and_scheme(
            allowed_hosts={self.request.get_host()},
            require_https= self.request.is_secure()
        ):
            return next_page
        
        return super().get_next_page()


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """View handling profile editing"""
    model = CustomUser
    template_name = 'core/profile_edit.html'
    
    def get_form_class(self):
        """form class based on the role"""
        if self.request.user.role =='parent':
            return ParentprofileEditForm
        else:
            return HealthWorkerProfileEditForm
        
    def get_object(self, queryset =None):
        """Esures that each user can edit there own profile"""
        return self.request.user
    
    def get_success_url(self):
        """redirect based on there role after successfull update"""
        if self.request.user.role == 'parent':
            return reverse_lazy('dashbord:parent_dashbord')
        else:
            return reverse_lazy('dashbord:health_worker_dashbord')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit {self.request.user.get_role_display()} Profile"
        context['user'] = self.request.user
        
        #role specific content 
        
        return context
    
    def form_valid(self, form):
        try:
            messages.success(self.request, "Your profile is successfully updated")
            response = super().form_valid(form)
            
            # AJAX handling
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': "Your profile has been successfully updated"
                })
            
            return response
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f"Error updating profile: {str(e)}"
                }, status=500)
            raise  # Re-raise exception 
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        print(f"Form errors: {form.errors}")  # Add this for debugging

        # If AJAX request, return JSON with errors
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': "Please correct the errors below",
                'errors': form.errors
            }, status=400)
            
        messages.error(self.request, "Please correct the errors below")
        return super().form_invalid(form)