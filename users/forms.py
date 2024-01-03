from django import forms
from django.db import connection

class LoginForm(forms.Form):
    userName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    
class PasswordResetForm(forms.Form):
    userName = forms.CharField(label = "User Name")
    
class RegForm(forms.Form):
    #performer or booker
    rolechoice = [("perform", "Performer"),("book","Booker")]
    
    #display name
    displayname = forms.CharField(max_length=20, strip=True,
                                label='Display Name',
                                help_text="This name is how the public will see you. Can't be changed after registration.. yet")
    
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
    rate = forms.DecimalField(max_digits=7, decimal_places=2, label="Hourly Rate", required=False)
    
    #Average Gigs per month (If Performer)
    averagegigs = forms.IntegerField(label='Average Gigs Per Month',
                                    help_text="How many performances do you normally conduct each month?",
                                    required=False)
    
    #Venue (drop down or create new) (If booker)
    venue = forms.ChoiceField(widget=forms.RadioSelect,
	                          choices=[(0,'Create New Venue Now'),(1,'Create or Join a Venue Later')],required=False,
	                          label="")
        #Name (If booker and creating new venue)
    venuename = forms.CharField(max_length=70, strip=True, required=False, label='Venue Name')
    
    #email (If booker and creating new venue)
    venueemail = forms.EmailField(max_length=50, required=False, label='Venue Email')
    
    #address (If booker and creating new venue)
    venueaddress = forms.CharField(max_length=50, strip=True, required=False, label='Venue Address')
    
    #phone number (If booker and creating new venue)
    venuephone = forms.CharField(max_length=15, strip=True, required=False, label='Venue Phone')
    
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
		
    #validation function to make sure field isn't blank
    def clean_rate(self):
        data = self.cleaned_data['rate']
        
        #check performer validation. Not required for bookers
        if self.data['role']=='perform':
            if self.data['rate']=='':
                raise forms.ValidationError("Fill in your usual hourly rate (this won't lock you into that price)")
        return data
    
    #validation function to make sure field isn't blank
    def clean_averagegigs(self):
        data = self.cleaned_data['averagegigs']
        
        #check performer validation. Not required for bookers
        if self.data['role']=='perform':
            if self.data['averagegigs']=='':
                raise forms.ValidationError("Fill in Average Gigs Per Month field")
        return data
		
		

