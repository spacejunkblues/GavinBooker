from django import forms
from django.db import connection

class AddPerformerForm(forms.Form):
    performers = forms.ChoiceField()