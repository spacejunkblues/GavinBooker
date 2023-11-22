from django import forms

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
    genre = forms.ChoiceField()
    
    #discription(If Performer)
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    
    #rate(If Performer)
    rate = forms.DecimalField(max_digits=7, decimal_places=2)
    
    #Venue (drop down or create new) (If booker)
    venue = forms.ChoiceField()
    
    #Name (If booker and creating new venue)
    venuename = forms.CharField(max_length=20, strip=True)
    
    #email (If booker and creating new venue)
    venueemail = forms.EmailField(max_length=20)
    
    #address (If booker and creating new venue)
    venueaddress = forms.CharField(max_length=50, strip=True)
    
    #phone number (If booker and creating new venue)
    venuephone = forms.CharField(max_length=15, strip=True)
        
