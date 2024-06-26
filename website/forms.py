from django import forms
from .models import EvaluationFormModel




class EvaluationForm(forms.ModelForm):
    tl_marks = forms.FloatField(min_value=0, max_value=10, label="Team Lead Marks out of 10")
    class Meta:
        model = EvaluationFormModel
        fields = ["tl_marks", "feedback"]
        exclude = ['hr_marks',"time_stamp","evaluation_for"]

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Select a CSV file")

