from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    file = forms.FileField(required=False)
    issue_type = forms.ChoiceField(
        choices=Report.ISSUE_TYPES, 
        required=False,
        label="Issue Type",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe the details of the issue here. If you chose "Others" in the previous field, please provide more details here.'}),
        required=True,
    )

    class Meta:
        model = Report
        fields = ["title","issue_type", "description", "file" ]  
        exclude = {"created_at"}
