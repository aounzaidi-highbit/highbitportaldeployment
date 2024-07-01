from django import forms
from .models import MVP, Activity, ActivityType
from website.models import Employee, Teams
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q


class EmployeeModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.employee_name} ({obj.role})"


class MVPForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "custom-char-field"}))
    plan = forms.CharField(widget=forms.Textarea(attrs={"class": "custom-plan-field"}))
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"})
    )

    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "custom-char-field"}),
    )
    current_phase = forms.ChoiceField(
        choices=[("MVP", "MVP"), ("Product", "Product")],
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

    class Meta:
        model = MVP
        fields = [
            "name",
            "plan",
            "start_date",
            "is_active",
            "end_date",
            "current_phase",
            "developers",
            "planners",
            "associates",
        ]

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
                team=user_team, mvp_role="Planner"
            ).exclude(employee_email=user_username)
            self.fields["associates"].queryset = Employee.objects.filter(
                team=user_team
            ).exclude(
                Q(mvp_role="Developer")
                | Q(mvp_role="Planner")
                | Q(employee_email=user_username)
                | Q(mvp_role="Growth Manager")
            )


class MVPFilterForm(forms.Form):
    teams = Teams.objects.all()
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "filter-box"}),
        required=False,
        label="Name",
    )
    team_name = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "Any")] + [(team.id, team.team_name) for team in teams],
        required=False,
        label="Team Name",
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"class": "filter-box", "type": "date"}),
        label="Start Date",
    )

    current_phase = forms.ChoiceField(
        widget=forms.TextInput(attrs={"class": "filter-box"}),
        choices=[("", "All"), ("MVP", "MVP"), ("Product", "Product")],
        required=False,
        label="Current Phase",
    )
    is_active = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "All"), ("true", "Yes"), ("false", "No")],
        required=False,
        label="Is Active",
    )

    activities = ActivityType.objects.all()
    activity_type = forms.ChoiceField(
        widget=forms.Select(attrs={"class": "filter-box"}),
        choices=[("", "All")]
        + [(activity.id, activity.name) for activity in activities],
        required=False,
        label="Activity Type",
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
                self.fields["mvp"].queryset = MVP.objects.filter(
                    team_name=employee.team
                )
            except Employee.DoesNotExist:
                self.fields["mvp"].queryset = MVP.objects.none()
