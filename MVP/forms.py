from django import forms
from .models import MVP, Activity, ActivityType, ShortUpdate
from website.models import Employee, Teams
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q
from django.core.validators import URLValidator
import re

class EmployeeModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.employee_name} ({obj.role})"


        
class MVPForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-plan-field"}), required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "custom-char-field"}))
    link = forms.CharField(  
        widget=forms.TextInput(attrs={"class": "custom-char-field"}),
        required=False,
    )
    plan = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-plan-field"}))
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"})
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"}),
    )
    development_starting_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"}),
    )
    status = forms.ChoiceField(
        choices=[("Active", "Active"), ("Pause", "Pause"), ("Completed", "Completed")],
        widget=forms.Select(attrs={"class": "custom-status-field"}),
    )
    current_phase = forms.ChoiceField(
        choices=[("","Select Phase"),("MVP", "MVP"), ("Product", "Product"), ("Failed", "Failed")],
        widget=forms.Select(attrs={"class": "custom-char-field"}),
    )
    developers = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    planners = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    associates = EmployeeModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    first_completion_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"}))
    class Meta:
        model = MVP
        fields = [
            "name",
            "link",
            "plan",
            "start_date",
            "status",
            "end_date",
            "development_starting_date",
            "first_completion_date",
            "current_phase",
            "developers",
            "planners",
            "associates",
        ]
        
    def clean_link(self):
        link = self.cleaned_data.get('link')
        if not link:
            return link

        if link and not (link.startswith('http://') or link.startswith('https://')):
            link = 'http://' + link 
        validator = URLValidator()
        try:
            validator(link)
        except forms.ValidationError:
            raise forms.ValidationError("Invalid URL")

        return link
    
    def save(self, commit=True):
        mvp = super().save(commit=False)
        remarks = self.cleaned_data.get("remarks")
        
        changes = []
        if mvp.pk:
            previous = MVP.objects.get(pk=mvp.pk)
            for field in mvp._meta.fields:
                field_name = field.name
                old_value = getattr(previous, field_name)
                new_value = getattr(mvp, field_name)
                if old_value != new_value:
                    if field_name not in ["updated_by", "created_by", "is_archived"]:
                        if old_value is None:
                            update_info = f'set to "{new_value}"'
                        else:
                            update_info = f'changed from "{old_value}" to "{new_value}"'
                            
                        if mvp.updated_by:
                            updated_by_name = mvp.updated_by.employee_name
                        else:
                            updated_by_name = Employee.objects.get(employee_email=self.request.user.username).employee_name
                            
                        changes.append(f'{field.verbose_name}: {update_info} updated by "{updated_by_name}"')

                    
        if changes or remarks:
            activity_type = ActivityType.objects.get_or_create(name="Update")[0]
            changes_str = "\n".join(changes)
            activity = Activity(
                mvp=mvp,
                activity_type=activity_type,
                team_name=mvp.team_name,
                changes=changes_str,
                remarks=remarks,  
            )
            activity.save()

        if commit:
            mvp.save()
            self.save_m2m()
        return mvp
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(MVPForm, self).__init__(*args, **kwargs)

        if self.request:
            user_username = self.request.user.username
            employee = Employee.objects.get(employee_email=user_username)
            user_team = employee.team
            self.fields["developers"].queryset = Employee.objects.filter(
                team=user_team, mvp_role="Developer"
            ).exclude(employee_email=user_username)
            self.fields["planners"].queryset = Employee.objects.filter(
                mvp_role="Planner"
            ).exclude(employee_email=user_username)
            self.fields["associates"].queryset = Employee.objects.filter(
                team=user_team
            ).exclude(
                Q(mvp_role="Developer")
                | Q(mvp_role="Planner")
                | Q(employee_email=user_username)
                | Q(mvp_role="Growth Manager")
            )

    
    def clean_first_completion_date(self):
        if self.instance.pk and self.instance.first_completion_date:
            return self.instance.first_completion_date
        return self.cleaned_data['first_completion_date']
    
    def clean(self):
        cleaned_data = super().clean()
        developers = cleaned_data.get('developers')
        start_date = cleaned_data.get('start_date')
        development_starting_date = cleaned_data.get('development_starting_date')
        planners = cleaned_data.get('planners')
        status = cleaned_data.get('status')
        first_completion_date = cleaned_data.get('first_completion_date')
        
        if developers and not development_starting_date:
            self.add_error('development_starting_date', 'Development starting date is required if developers are selected.')
        if development_starting_date and not developers:
            self.add_error('developers', 'Developers are required if development starting date is selected.')
        if start_date and not planners:
            self.add_error('planners', 'Planners are required if start date is selected.')
        if status == "Completed" and not first_completion_date:
            self.add_error('first_completion_date', 'First completion date is required if status is completed.')
        
        return cleaned_data

class MVPFilterForm(forms.Form):
    teams = Teams.objects.all()

    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "filter-box"}),
        required=False,
        label="Name",
    )
    team_name = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "team-filter-box"}),
        choices=[("", "Any")] + [(team.id, team.team_name) for team in teams],
        required=False,
        label="Team Name",
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class": "filter-box", "type": "date"}),
        label="Start Date",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class": "filter-box", "type": "date"}),
        label="End Date",
    )
    current_phase = forms.ChoiceField(
        widget=forms.TextInput(attrs={"class": "filter-box"}),
        choices=[("", "All"), ("MVP", "MVP"), ("Product", "Product")],
        required=False,
        label="Current Phase",
    )

    status= forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "All"), ("Active", "Active"), ("Pause", "Pause"), ("Completed", "Completed")],
        required=False,
        label="Status",
    )
    activities = ActivityType.objects.all()
    activity_type = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "All")]
        + [(activity.id, activity.name) for activity in activities],
        required=False,
        label="Activity Type",
    )

class ShortUpdateFilterForm(forms.Form):
    teams = Teams.objects.all()
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "filter-box"}),
        required=False,
        label="Title",
    )
    team_name = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "team-filter-box"}),
        choices=[("", "Any")] + [(team.id, team.team_name) for team in teams],
        required=False,
        label="Team Name",
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class": "filter-box", "type": "date"}),
        label="Start Date",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class": "filter-box", "type": "date"}),
        label="End Date",
    )
    status = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "All"), ("Success", "Success"), ("Fail", "Fail"), ("Pending", "Pending")],
        required=False,
        label="Status",
    )

class ActivityTypeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "custom-act-text-field"})
    )

    class Meta:
        model = ActivityType
        fields = ["name"]


class ActivityForm(forms.ModelForm):
    mvp = forms.ModelChoiceField(
        queryset=MVP.objects.all(),
        widget=forms.Select(attrs={"class": "custom-act-field"}),
    )
    activity_type = forms.ModelChoiceField(
        queryset=ActivityType.objects.all(),
        widget=forms.Select(attrs={"class": "custom-act-field"}),
    )
    changes = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-notes-text-field"}),required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-notes-text-field"}))
    class Meta:
        model = Activity
        fields = ["mvp", "activity_type", "notes"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(ActivityForm, self).__init__(*args, **kwargs)
        if user:
            try:
                employee = Employee.objects.get(employee_email=user.username)
                if employee.mvp_role == "Planner":
                    self.fields["mvp"].queryset = MVP.objects.filter(
                        planners=employee, is_archived=False
                    )
                else:
                    self.fields["mvp"].queryset = MVP.objects.filter(
                    team_name=employee.team, is_archived=False
                    )
            except Employee.DoesNotExist:
                self.fields["mvp"].queryset = MVP.objects.none()
                
class ShortUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[("","Select Status"),("Success", "Success"), ("Fail", "Fail"), ("Pending", "Pending")],
        widget=forms.Select(attrs={"class": "custom-status-field"}),
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "custom-char-field"})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "custom-plan-field"})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"}),
    )
    
    class Meta:
        model = ShortUpdate
        fields = ["status", "title", "description", "start_date", "end_date"]