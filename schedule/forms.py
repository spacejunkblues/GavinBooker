from django import forms

class TimeInput(forms.TimeInput):
    input_type='time'

class AddAvailabilityForm(forms.Form):
    start = forms.TimeField(widget=TimeInput)
    end = forms.TimeField(widget=TimeInput)
    location = forms.CharField(max_length=50)
    
    
class BookingForm(forms.Form):
    start = forms.TimeField(widget=TimeInput)
    end = forms.TimeField(widget=TimeInput)
    payment = forms.DecimalField(max_digits=7, decimal_places=2)
    condition = forms.CharField(widget=forms.Textarea,max_length=200)