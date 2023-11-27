from django import forms
from django.db import connection

class LoginForm(forms.Form):
    userName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    
class RegForm(forms.Form):
    #performer or booker
    rolechoice = [("perform", "Performer"),("book","Booker")]
    
    #display name
    displayname = forms.CharField(max_length=20, strip=True)
    
    #email
    email = forms.EmailField(max_length=50)
    
    #phone number
    phone = forms.CharField(max_length=15, strip=True)
    
    #choose role. 
    role = forms.ChoiceField(choices=rolechoice)
    
    #Genre played (If Performer) The choices will be pulled from the database in the view
    genre = forms.ChoiceField(required=False)
    
    #discription(If Performer)
    description = forms.CharField(widget=forms.Textarea, max_length=200, required=False)
    
    #rate(If Performer)
    rate = forms.DecimalField(max_digits=7, decimal_places=2, required=False)
    
    #Venue (drop down or create new) (If booker)
    venue = forms.ChoiceField(required=False)
    
    #Name (If booker and creating new venue)
    venuename = forms.CharField(max_length=20, strip=True, required=False)
    
    #email (If booker and creating new venue)
    venueemail = forms.EmailField(max_length=20, required=False)
    
    #address (If booker and creating new venue)
    venueaddress = forms.CharField(max_length=50, strip=True, required=False)
    
    #phone number (If booker and creating new venue)
    venuephone = forms.CharField(max_length=15, strip=True, required=False)
    
    #validation function to make sure field isn't blank
    def clean_venuename(self):
        data = self.cleaned_data['venuename']
        
        #don't need to check performer validation. All performer specific fields are optional
        if self.data['role']=='book':
            #0 means the user is creating a new venue. If user isn't creating a new venue, then no need to validate
            if self.data['venue']=='0':
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
    
    #validation function to make sure field isn't blank
    def clean_venueemail(self):
        data = self.cleaned_data['venueemail']
        
        #don't need to check performer validation. All performer specific fields are optional
        if self.data['role']=='book':
            #0 means the user is creating a new venue. If user isn't creating a new venue, then no need to validate
            if self.data['venue']=='0':
                if self.data['venueemail']=='':
                    raise forms.ValidationError("Fill in Venue Email")
        return data
      
    #validation function to make sure field isn't blank      
    def clean_venueaddress(self):
        data = self.cleaned_data['venueaddress']
        
        #don't need to check performer validation. All performer specific fields are optional
        if self.data['role']=='book':
            #0 means the user is creating a new venue. If user isn't creating a new venue, then no need to validate
            if self.data['venue']=='0':
                if self.data['venueaddress']=='':
                    raise forms.ValidationError("Fill in Venue Address")
        return data

    #validation function to make sure field isn't blank
    def clean_venuephone(self):
        data = self.cleaned_data['venuephone']
        
        #don't need to check performer validation. All performer specific fields are optional
        if self.data['role']=='book':
            #0 means the user is creating a new venue. If user isn't creating a new venue, then no need to validate
            if self.data['venue']=='0':
                if self.data['venuephone']=='':
                    raise forms.ValidationError("Fill in Venue Phone")
        return data
