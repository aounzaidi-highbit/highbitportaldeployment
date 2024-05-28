from django.contrib import admin
from .models import Employee, EvaluationFormModel, Teams
from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Register your models here.

admin.site.site_title = "Highbit HR Admin Panel"
admin.site.site_header = "HR Admin Panel"


class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ["username"]

class IsTeamLeadFilter(admin.SimpleListFilter):
    title = "Team Lead"
    parameter_name = "team_lead"

    def lookups(self, request, model_admin):
        team_lead_names = Employee.objects.filter(is_team_lead=True).values_list(
            "employee_name", flat=True
        )
        return [(name, name) for name in team_lead_names]

    def queryset(self, request, queryset1):
        if self.value():
            print(self.value())
            return Employee.objects.filter(team_lead__employee_name=self.value())

        else:
            return queryset1

class EmployeeInformation(admin.ModelAdmin):
    list_display = ("employee_id", "employee_name", "team", "team_lead")
    search_fields = ["employee_id", "employee_name"]
    list_filter = ["team", "is_team_lead", IsTeamLeadFilter]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "team_lead":
            kwargs["queryset"] = Employee.objects.filter(is_team_lead=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

def send_evaluation_email(modeladmin, request, queryset):
    for evaluation in queryset:
        employee = evaluation.employee
        team_lead_name = (
            employee.team_lead.employee_name if employee.team_lead else "N/A"
        )
        email_template = "evaluation_email.html"
        context = {
            "employee_name": employee.employee_name,
            "team_lead_name": team_lead_name,
            "evaluation_for": evaluation.evaluation_for,
            "hr_marks": evaluation.hr_marks,
            "tl_marks": evaluation.tl_marks,
            "weightage": evaluation._weighted_average,
            "feedback": evaluation.feedback,
        }
        html_message = render_to_string(email_template, context)
        plain_message = strip_tags(html_message)
        performance_review = f"Performance Review for {evaluation.evaluation_for}"
        send_mail(
            performance_review,
            plain_message,
            "your_email@example.com",
            [employee.employee_email],
            html_message=html_message,
        )

send_evaluation_email.short_description = "Send evaluation email to selected employees"

class EvaluationFormModelAdmin(admin.ModelAdmin):
    list_display = [
        "employee_id",
        "employee",
        "employee_email",
        "evaluated_by",
        "evaluation_for",
        "evaluation_date",
        "get_weighted_average",
    ]
    actions = [send_evaluation_email]

    search_fields=['evaluation_date']
    def get_weighted_average(self, obj):
        return obj._weighted_average

    def employee_id(self, obj):
        return obj.employee_id

    def employee_email(self, obj):
        return obj.employee.employee_email

    get_weighted_average.short_description = "Weighted Average"


admin.site.register(Teams)
admin.site.register(Employee, EmployeeInformation)
admin.site.register(EvaluationFormModel, EvaluationFormModelAdmin)
