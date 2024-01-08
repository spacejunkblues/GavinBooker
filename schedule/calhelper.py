from datetime import datetime
from calendar import Calendar

class MonthCal:
    def __init__(self, month = datetime.now().month, year = datetime.now().year):
        self.month=month
        self.year=year
        
        #get current day to highlight on calendar
        self.current_m=datetime.now().month
        self.current_y=datetime.now().year
        self.current_d=datetime.now().day
        
        #init a Calendar object to get dates from
        cal = Calendar(firstweekday=6) #6 is Sunday
        
        #define days of the week
        self.weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        #get list of dates for current month
        self.dates = cal.monthdayscalendar(self.year,self.month)
        
        #setup month name coverter
        self.month_converter={1:'January', 2:'February', 3:'March', 4:'April',\
                            5:'May', 6:'June', 7:'July', 8:'August',\
                            9:'September', 10:'October', 11:'November', 12:'December'}
        
        #set the name of the current month
        self.monthname = self.month_converter[self.month]
     
        #set next and previous months
        self.setNextPreviousMonth()
        
        #events stores each availability or booking event from a given day
        self.events={}
        for week in self.dates:
            for day in week:
                if day != 0:
                    self.events[day] = None


    def setNextPreviousMonth(self):
        #get next month
        self.nextmonth = self.month + 1
        self.nextyear = self.year
        
        #check to for year roll over
        if(self.nextmonth == 13):
            self.nextmonth = 1
            self.nextyear = self.year + 1
            
        #get previous month
        self.previousmonth = self.month - 1
        self.previousyear = self.year
        
        #check to for year roll over
        if(self.previousmonth == 0):
            self.previousmonth = 12
            self.previousyear = self.year - 1


    #function that will convert the month number to a month name
    def ConvertMonthtoName(self, month_num):
        return self.month_converter[month_num]


    def addEvent(self, event_id, day, start, end, displayname, status = None):
        #if this is the first time an event is added. start a list
        if self.events[day] == None:
            self.events[day] = []
        
        #add event info the event list for that day
        self.events[day].append({'id': event_id, 'start': start, 'end':end, 'displayname':displayname, 'status':status})
        
        
    #this function formats the calendar using the list given from the Calendar object
    #It adds all the events that have been added up to this point
    def buildCalendar(self):
        self.cal_data = []
        for week in self.dates:
            #Builds each day of the week. Formats the data in a dict of date and events
            self.cal_data.append([{'date':day,'events':self.events[day]} if day != 0 else None for day in week])
        return self.cal_data
        
    