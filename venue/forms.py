from django import forms
from django.db import connection
		
class CreateVenueForm(forms.Form):
    #Name (If booker and creating new venue)
    venuename = forms.CharField(max_length=70, strip=True, required=True, label='Venue Name')
    
    #email (If booker and creating new venue)
    venueemail = forms.EmailField(max_length=50, required=True, label='Venue Email')
    
    #address (If booker and creating new venue)
    venueaddress = forms.CharField(max_length=50, strip=True, required=True, label='Venue Address')
    
    #phone number (If booker and creating new venue)
    venuephone = forms.CharField(max_length=15, strip=True, required=True, label='Venue Phone')

    def __init__(self, *args, **kwargs):
        super(CreateVenueForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    #validation function to make sure field isn't blank
    def clean_venuename(self):
        data = self.cleaned_data['venuename']

        #name can't be blank
        if self.data['venuename']=='':
            raise forms.ValidationError("Fill in Venue Name")
                    
        #name has to be unique
        #get database cursor
        cursor = connection.cursor()
                
        #get names from database
        cursor.execute("SELECT name \
                        FROM Venue")
                                
        #check to see if name taken
        for name in cursor.fetchall():
            if name[0] == data:
                raise forms.ValidationError("Venue name already exists.")
                break
                
        return data
