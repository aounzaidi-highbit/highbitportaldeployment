import datetime
from django import forms
from django.utils.translation import gettext_lazy as _
from core.settings import DEFAULT_AUTO_FIELD
from .models import EvaluationFormModel


MONTH_CHOICES = (
    ("January", _("January")),
    ("February", _("February")),
    ("March", _("March")),
    ("April", _("April")),
    ("May", _("May")),
    ("June", _("June")),
    ("July", _("July")),
    ("August", _("August")),
    ("September", _("September")),
    ("October", _("October")),
    ("November", _("November")),
    ("December", _("December")),
)

class EvaluationForm(forms.ModelForm):
    tl_marks = forms.FloatField(min_value=0, max_value=10, label="Team Lead Marks out of 10")
    hr_marks = forms.FloatField(
        max_value=10, min_value=0, required=False, label="HR Marks out of 10"
    )
    evaluation_for = forms.ChoiceField(choices=MONTH_CHOICES, label="Evaluation For")
        
    class Meta:
        model = EvaluationFormModel
        fields = ["tl_marks", "hr_marks", "evaluation_for", "feedback"]

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select a CSV file")
