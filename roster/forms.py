from django import forms

class AddPerformerForm(forms.Form):
    performers = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(AddPerformerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
class InvitePerformerForm(forms.Form):
    email = forms.EmailField(max_length=50, label="Performer's Email")

    def __init__(self, *args, **kwargs):
        super(InvitePerformerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'