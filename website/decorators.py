# decorators.py
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import Employee

def roles_required(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    employee = Employee.objects.filter(employee_email=request.user.username).first()
                    if employee and employee.mvp_role in roles:
                        return view_func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden("You do not have permission to access this page.")
                except Employee.DoesNotExist:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            else:
                return redirect('home')
        return _wrapped_view
    return decorator