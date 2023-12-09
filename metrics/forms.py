from django import forms

class ProblemForm(forms.Form):
    severeOptions = ((1,'Unusable if not fixed'),(2,'An annoying issue'),(3,'An improvement idea'))
    
    subject = forms.CharField(max_length=50)    
    severity = forms.ChoiceField(choices=severeOptions)
    comment = forms.CharField(widget=forms.Textarea,max_length=200)