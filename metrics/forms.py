from django import forms

class ProblemForm(forms.Form):
    severeOptions = ((1,'Unusable if not fixed'),(2,'An annoying issue'),(3,'An improvement idea'))
    
    subject = forms.CharField(max_length=50)    
    severity = forms.ChoiceField(choices=severeOptions)
    comment = forms.CharField(widget=forms.Textarea,max_length=200)

    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'