from django import forms
from django.shortcuts import render

class TimeInput(forms.TimeInput):
    input_type='time'

#concates and formats the time to be stored like a timefield    
#this function is needed with TimePickerWidget
def convert_time(data, name):
    #init 
    hourName = f'{name}_hour'
    minuteName = f'{name}_minute'
    ampmName = f'{name}_ampm'
    
    #Only hour will change
    hour = data[hourName]
    
    #format hour
    if data[ampmName] == 'AM' and data[hourName] == '12':
        hour = '00'
    elif data[ampmName] == 'PM' and data[hourName] != '12':
        hour = int(data[hourName]) + 12
        
    #change HH:MM AM format to HH:MM:SS
    data = f"{hour}:{data[minuteName]}:00"
    
    return data

#This is custom widget that turns a timefield in a Time Picker
#Needs timeinput.css and custom clean_item function to work
#note that the time returned is a string and not a datetime 
#   ---(maybe add that feature to the covert_time function later)
class TimePickerWidget(forms.widgets.TimeInput):
    def render(self, name, value, attrs=None, renderer=None):
        #init choices
        hourchoice = [("01", "01"),
                        ("02","02"),
                        ("03","03"),
                        ("04","04"),
                        ("05","05"),
                        ("06","06"),
                        ("07","07"),
                        ("08","08"),
                        ("09","09"),
                        ("10","10"),
                        ("11","11"),
                        ("12","12")]
        minutechoice = [("00", "00"),
                        ("05","05"),
                        ("10","10"),
                        ("15","15"),
                        ("20","20"),
                        ("25","25"),
                        ("30","30"),
                        ("35","35"),
                        ("40","40"),
                        ("45","45"),
                        ("50","50"),
                        ("55","55")]
        ampmchoice = [("AM", "AM"),("PM","PM")]
        
        #build picker boxes
        hour = forms.ChoiceField(choices=hourchoice)
        minute = forms.ChoiceField(choices=minutechoice)
        ampm = forms.ChoiceField(choices=ampmchoice)
    
        #change picker boxes class for syling
        hour.widget.attrs.update({"class": "time-picker_select"})
        minute.widget.attrs.update({"class": "time-picker_select"})
        ampm.widget.attrs.update({"class": "time-picker_select"})

        #change picker boxs names to make them unique to thier object
        hourName = f'{name}_hour'
        minuteName = f'{name}_minute'
        ampmName = f'{name}_ampm'
        
        #value will be None if no inital time is passed
        if value == None:
            value = "00:00:00"
            
        #initial drop down times
        hourValue = value[0:2]
        minuteValue = value[3:5]
        ampmValue = 'AM'
        
        if int(hourValue)>11:
            ampmValue = 'PM'
        if int(hourValue) > 12:
            hourValue = int(hourValue)-12

        return f'<div class="time-inputbox"> \
                    {super().render(name, value, attrs=None, renderer=None)} \
                </div> \
                <div class="time-picker"> \
                    {name[0].upper()}{name[1:]} \
                    {hour.widget.render(hourName,hourValue)} \
                    : {minute.widget.render(minuteName,minuteValue)} \
                    {ampm.widget.render(ampmName,ampmValue)} \
                </div>'


class AddAvailabilityForm(forms.Form):
    start = forms.TimeField(widget=TimePickerWidget, label='')
    end = forms.TimeField(widget=TimePickerWidget, label='')
    location = forms.CharField(max_length=50)
   
    #This is required to make the timepicker widget to work. Each field needs to be overwritten
    def clean_start(self):
        return convert_time(self.data,"start")
        
    def clean_end(self):
        return convert_time(self.data,"end")
        
       
class BookingForm(forms.Form):
    
    start = forms.TimeField(widget=TimePickerWidget, label='') #label is handled by the widget
    end = forms.TimeField(widget=TimePickerWidget, label='')
    payment = forms.DecimalField(max_digits=7, decimal_places=2)
    condition = forms.CharField(widget=forms.Textarea,max_length=200)
     
    #This is required to make the timepicker widget to work. Each field needs to be overwritten
    def clean_start(self):
        return convert_time(self.data,"start")
        
    def clean_end(self):
        return convert_time(self.data,"end")
    