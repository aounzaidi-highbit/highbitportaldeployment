from django import forms
from .models import MVP, Activity
from website.models import Employee, Teams
from django.forms.widgets import CheckboxSelectMultiple

class MVPForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    
    developers = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(), 
        widget=CheckboxSelectMultiple
    )
    planners = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(), 
        widget=CheckboxSelectMultiple
    )
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = MVP
        fields = ['name', 'start_date', 'is_active', 'end_date', 'current_phase', 'developers', 'planners', ]  

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MVPForm, self).__init__(*args, **kwargs)
        
        if self.request:
            user_username= self.request.user.username
            employee = Employee.objects.get(employee_email=user_username)
            user_team = employee.team
            self.fields['developers'].queryset = Employee.objects.filter(team=user_team, mvp_role='Developer').exclude(employee_email=user_username)
            self.fields['planners'].queryset = Employee.objects.filter(team=user_team, mvp_role='Planner').exclude(employee_email=user_username)
            

class MVPFilterForm(forms.Form):
    teams=Teams.objects.all()
    name = forms.CharField(required=False, label='Name')
    team_name = forms.ChoiceField(choices=[('', 'Any')]+[(team.id, team.team_name) for team in teams], required=False, label='Team Name')
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}), label='Start Date')
    current_phase = forms.ChoiceField(choices=[('', 'Any'), ('MVP','MVP'), ('Product', 'Product')],required=False, label='Current Phase')
    is_active = forms.ChoiceField(choices=[('', 'Any'), ('true', 'Yes'), ('false', 'No')], required=False, label='Is Active')
  
            
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['mvp', 'activity_type', 'notes']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ActivityForm, self).__init__(*args, **kwargs)
        if user:
            try:
                employee = Employee.objects.get(employee_email=user.username)
                self.fields['mvp'].queryset = MVP.objects.filter(team_name=employee.team)
            except Employee.DoesNotExist:
                self.fields['mvp'].queryset = MVP.objects.none()