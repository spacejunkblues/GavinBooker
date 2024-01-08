from django import forms

class ReviewForm(forms.Form):
    #rating1 = forms.MultipleChoiceField([('1','HI')])
    
    ratingOptions = ((1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'))
    rating = forms.ChoiceField(choices=ratingOptions)
    comment = forms.CharField(widget=forms.Textarea,max_length=200)

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'