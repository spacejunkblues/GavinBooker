from django import forms

class AddPerformerForm(forms.Form):
    performers = forms.ChoiceField()
    
    
class InvitePerformerForm(forms.Form):
    email = forms.EmailField(max_length=50, label="Performer's Email")