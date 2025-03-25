from django.shortcuts import redirect
from django.urls import reverse_lazy


class RoleBasedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response #automatically passed with django framework
        
        
    def __call__(self, request):
        """callable method to handle specifics user requests"""
        #skip for admin, statics and non-get requests 
        if (
            request.path.startswith('/admin/') or 
            request.path.startswith('/static/') or
            request.method != 'GET'
        ):
            return self.get_response(request)
        
        if (
            request.user.is_authenticated and 
            request.path in ['/', '/register/','/login/']
        ):
            if request.user.role == 'parent':
                return redirect(reverse_lazy('dashbord:parent_dashbord'))
            if request.user.role == 'health_worker':
                return redirect(reverse_lazy('dashbord:health_worker_dashbord'))
            
        return self.get_response(request)