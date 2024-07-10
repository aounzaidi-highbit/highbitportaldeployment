from django.urls import reverse
from website.models import Employee

def mvp_role_permission(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(employee_email=request.user.username).first()
        if employee:
            return {"logged_in_user_role": employee}
        else:
            return {"logged_in_user_role": None}
    return {}

