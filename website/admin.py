from django.contrib import admin
from .models import Employee, EvaluationFormModel, Teams, AdminFeautures
from django import forms

# Register your models here.

admin.site.site_title = "Highbit HR Admin Panel"
admin.site.site_header = "HR Admin Panel"


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


class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ["username"]


class EmployeeInformation(admin.ModelAdmin):
    list_display = ("employee_id", "employee_name", "team", "team_lead")
    search_fields = ["employee_id", "employee_name"]
    list_filter = ["team", "is_team_lead", IsTeamLeadFilter]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "team_lead":
            kwargs["queryset"] = Employee.objects.filter(is_team_lead=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    list_filter = ["evaluation_for"]
    search_fields = ["evaluation_date"]

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
admin.site.register(AdminFeautures)
