from django import forms

class TimeInput(forms.TimeInput):
    input_type='time'

class AddAvailabilityForm(forms.Form):
    start = forms.TimeField(widget=TimeInput)
    end = forms.TimeField(widget=TimeInput)
    location = forms.CharField()
    
    
class BookingForm(forms.Form):
    start = forms.TimeField(widget=TimeInput)
    end = forms.TimeField(widget=TimeInput)
    payment = forms.FloatField()
    condition = forms.CharField()