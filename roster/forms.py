from django import forms

class AddPerformerForm(forms.Form):
    performers = forms.ChoiceField()