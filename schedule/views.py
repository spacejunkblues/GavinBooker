from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . calhelper import MonthCal
from django.db import connection
from . forms import AddAvailabilityForm, BookingForm
import datetime
from django.contrib import messages
from metrics.loghelper import log_visit

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


#helper function that standardizes the format of times on the calendar
def format_addevent(cursor, cal, include_status=True, include_displayname=False):
    #add event to the calendar
    for event in dictfetchall(cursor):
        #get ID
        event_id = event['availability_id']
        
        #get day of the month as a number
        day = int(event['start_time'].strftime('%d'))
        
        #get start time
        start = event['start_time'].strftime('%I') +\
                ":" + event['start_time'].strftime('%M') +\
                " " + event['start_time'].strftime('%p')
        
        #get end
        end = event['end_time'].strftime('%I') +\
                ":" + event['end_time'].strftime('%M') +\
                " " + event['end_time'].strftime('%p')
        
        #add the optional displayname
        displayname = ''
        if include_displayname:
            displayname = event['displayname']
        
        
        if include_status:
            #get status of bookings
            status = event['status_type']
            
            #add the event to the object
            cal.addEvent(event_id, day, start, end, displayname,  status)
        else: 
            #availabilities
            cal.addEvent(event_id, day, start, end, displayname)

def add_performer_events(id, cal):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT * FROM performers_avail \
                    WHERE EXTRACT(MONTH FROM start_time) = %s AND \
                            EXTRACT(YEAR FROM start_time) = %s AND\
                            django_id = %s;",[cal.month,cal.year, id])

    #add availabilites to calendar
    format_addevent(cursor, cal, include_status=False)
        
    #get performer id from the django ID
    cursor.execute("SELECT performer_ID \
                    FROM Performer NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[id])
    performer_id = cursor.fetchone()
    
    #send query to get all booked gigs.
    cursor.execute("SELECT * FROM performers_booked NATURAL JOIN Status \
                    WHERE EXTRACT(MONTH FROM start_time) = %s AND \
                        EXTRACT(YEAR FROM start_time) = %s AND \
                        performer_ID = %s;",[cal.month,cal.year, performer_id])
    
    #add bookings to the calendar
    format_addevent(cursor, cal, include_status=True)
    
def add_booker_events(id, cal):
    #Connect to the database
    cursor = connection.cursor()
    
    #get Booker id from the django ID
    cursor.execute("SELECT booker_ID \
                    FROM Booker NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[id])
    booker_id = cursor.fetchone()
    
    #send a query to get all availabilities
    cursor.execute("SELECT * FROM bookers_options \
                    WHERE EXTRACT(MONTH FROM start_time) = %s AND \
                            EXTRACT(YEAR FROM start_time) = %s AND\
                            booker_ID = %s;",[cal.month,cal.year, booker_id])
    
    #add availabilites to calendar
    format_addevent(cursor, cal, include_status=False, include_displayname=True)
    
    #send query to get all booked gigs.
    cursor.execute("SELECT * FROM bookers_booked NATURAL JOIN Status \
                    WHERE EXTRACT(MONTH FROM start_time) = %s AND \
                        EXTRACT(YEAR FROM start_time) = %s AND \
                        booker_ID = %s;",[cal.month,cal.year, booker_id])
    
    #add bookings to the calendar
    format_addevent(cursor, cal, include_status=True, include_displayname=True)

#gets the role of the given user from the database
def get_role(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT role_ID FROM User_tbl \
                    WHERE django_ID = %s",[id])
    
    return cursor.fetchone()[0]    

@login_required(login_url='/users/login_user')
def calendar_view(request, year ='', month='', *args, **kwargs):
    #log the visit
    log_visit(request.user.id,"Calendar", None)

    #get month object
    if year != '' and month != '':
        cal = MonthCal(year = year, month = month)
    else:
        cal = MonthCal() #pulls current month by default
    
    #get role
    role_id = get_role(request.user.id)
    
    if role_id == 1: #1 is Performer
        #add all performer events from the database to the calendar
        add_performer_events(request.user.id, cal)
    elif role_id == 2: #2 is Booker
        #add all booker events from the database to the calendar
        add_booker_events(request.user.id, cal)
    
    #preps the calendar for html parsing
    cal.buildCalendar()
        
    #wrap the calendar in a dict to send out for rendering
    context = {'month':cal, 'role':role_id}
    
    return render(request, 'calendar.html', context)


def get_performer_details(request, id):
    #Connect to the database
    cursor = connection.cursor()
    
    #get performer id from the django ID
    cursor.execute("SELECT performer_ID \
                    FROM Performer NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[request.user.id])
    performer_id = cursor.fetchone()
    
    #send a query to get all availabilities
    cursor.execute("SELECT start_time, end_time, location \
                    FROM performers_avail \
                    WHERE availability_ID = %s AND \
                        performer_ID = %s",[id, performer_id])

    #store query result
    cols = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    
    #if row is empty, check to see if it's a booked gig instead
    if row == None:
        #send query to get all booked gigs.
        cursor.execute("SELECT status_id, status_type, payment, condition, start_time, end_time, \
                            name, address, displayname, email \
                        FROM performers_booked NATURAL JOIN Status \
                        WHERE availability_ID = %s AND \
                            performer_ID = %s",[id, performer_id])
        #store query result
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        
        #No result
        if row == None:
            return redirect('/')
    
    #store query result into a dictionary
    detail_info = dict(zip(cols, row))
    
    #--- check for post after this point ---
    #otherwise, one performer could accept bookings for another
    if request.method == "POST":
        #There is a booking associated with this availability
        if 'status_id' in detail_info.keys():
        
            #ensure that only pending events ('Offered') can POST, anything after performers can't modify
            if detail_info['status_id']!=1:
                return redirect('/')
        
            #init new_status
            new_status = detail_info['status_id']
            
            if 'accept' in request.POST.keys():
                new_status = 2 #this means the gig is booked
            if 'decline' in request.POST.keys():
                new_status = 3 #this means the gig is cancelled
        
            #update the new status in the bookings table
            cursor.execute("UPDATE Bookings \
                            SET status_ID = %s \
                            WHERE availability_ID = %s",
                            [new_status, id])
            
            #redirect back to the same detail page, which will refresh the page with new status
            return redirect('/schedule/detail/' + str(id))
       
        #There is no status, so it's just an availbility at this point
        #allow performer to delete
        elif 'delete' in request.POST.keys():
            #Delete selected availability
            cursor.execute("DELETE FROM Availability \
                            WHERE availability_ID = %s",
                            [id])
            return redirect('/')
        
    #wrap the info in a dict to send out for rendering
    context = {'obj':detail_info}
    
    return render(request, 'detail.html', context)


def get_booker_details(request, id):
    #Connect to the database
    cursor = connection.cursor()
    
    #get performer id from the django ID
    cursor.execute("SELECT booker_ID \
                    FROM Booker NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[request.user.id])
    booker_id = cursor.fetchone()
    
    #send a query to get all availabilities
    cursor.execute("SELECT rate, start_time, end_time, location, displayname \
                    FROM bookers_options \
                    WHERE availability_ID = %s AND \
                        booker_ID = %s",[id, booker_id])

    #store query result
    cols = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    
    #if row is empty, check to see if it's a booked gig instead
    if row == None:
        #send query to get all booked gigs.
        cursor.execute("SELECT status_id, status_type, payment, condition, start_time, end_time, displayname \
                        FROM bookers_booked NATURAL JOIN Status \
                        WHERE availability_ID = %s AND \
                            booker_ID = %s",[id, booker_id])
        #store query result
        cols = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        
        #No result
        if row == None:
            return redirect('/')
    
    #store query result into a dictionary
    detail_info = dict(zip(cols, row))
    
    #--- check for post after this point ---
    #otherwise, one performer could accept bookings for another
    if request.method == "POST":
        if 'status_id' in detail_info.keys():
            #Looking at a booked detail
        
            #ensure that only booked events can POST
            if detail_info['status_id']!=2:
                return redirect('/')
        
            #init new_status
            new_status = detail_info['status_id']
            
            if 'complete' in request.POST.keys():
                new_status = 4 #this means the gig has been completed
            if 'cancel' in request.POST.keys():
                new_status = 3 #this means the gig is cancelled
            
            #update the new status in the bookings table
            cursor.execute("UPDATE Bookings \
                            SET status_ID = %s \
                            WHERE availability_ID = %s",
                            [new_status, id])
        
            #redirect back to the same detail page, which will refresh the page with new status
            return redirect('/schedule/detail/' + str(id))
        
        elif 'offer' in request.POST.keys():
            #Looking at an option
            form = BookingForm(request.POST)
            
            #Data is valid (data types are correct)
            if form.is_valid():
                #break out data
                start = form.cleaned_data['start']
                end = form.cleaned_data['end']
                payment = form.cleaned_data['payment']
                condition = form.cleaned_data['condition']
                
                #get month and year from the old start_time
                year=int(detail_info['start_time'].strftime('%Y'))
                month=int(detail_info['start_time'].strftime('%m'))
                day=int(detail_info['start_time'].strftime('%d'))
                
                #format times into datetimes
                start = datetime.datetime(year, month, day,
                                          int(start.strftime('%H')),
                                          int(start.strftime('%M')))
                end = datetime.datetime(year, month, day,
                                          int(end.strftime('%H')),
                                          int(end.strftime('%M')))
                

                #Offer the booking to the performer
                cursor.execute("CALL bookPerformer(%s,%s,%s,%s,%s,%s)",
                                [booker_id, id, payment, condition, start, end])
                
                #redirect to calendar view
                return redirect('/schedule/' + str(year) + '/' + str(month))
        
    else:
            form = BookingForm()
        
    #wrap the info in a dict to send out for rendering
    context = {'obj':detail_info, 'form':form}
    
    return render(request, 'bookerdetail.html', context)

@login_required(login_url='/users/login_user')
def detail_view(request, id, *args, **kwargs):
    #log the visit
    log_visit(request.user.id,"Detail", id)
    
    if get_role(request.user.id) == 1:#Performers
        return get_performer_details(request,id)
    else: #Bookers
        return get_booker_details(request,id)
    

@login_required(login_url='/users/login_user')
def add_availability_view(request, year, month, day, *args, **kwargs):
    #don't let bookers add availabilities
    if get_role(request.user.id) == 2:
        return redirect('/schedule/' + str(year) + '/' + str(month))
    
    #log the visit
    log_visit(request.user.id,"Add", None)
        
    #check to see if the submit button was pressed
    if request.method == "POST":
        #initialize the form object
        form = AddAvailabilityForm(request.POST)
        
        #Data is valid (data types are correct)
        if form.is_valid():
            #break out data
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            location = form.cleaned_data['location']
            
            #format times into datetimes
            start = datetime.datetime(year, month, day,
                                      int(start.strftime('%H')),
                                      int(start.strftime('%M')))
            end = datetime.datetime(year, month, day,
                                      int(end.strftime('%H')),
                                      int(end.strftime('%M')))
            

            #Connect to the database
            cursor = connection.cursor()
            
            #get performer id from the django ID
            cursor.execute("SELECT performer_ID \
                            FROM Performer NATURAL JOIN User_tbl \
                            WHERE django_ID = %s;",[request.user.id])
            performer_id = cursor.fetchone()
            
            #insert availability
            cursor.execute("INSERT INTO Availability  \
                            VALUES (DEFAULT, %s, %s, %s, %s);",
                            [performer_id, start, end, location])
                            
            #let the performer what the next steps are
            messages.success(request, ('Your availability is now visible to bookers. Now just wait for an offer!'))
            
            #redirect to calendar view
            return redirect('/schedule/' + str(year) + '/' + str(month))
                
    else:
        #This else handles initail vist to page (ei, Get request)
        form = AddAvailabilityForm()

    #wrap the form in a dict to send out for rendering
    context = {'form':form}
    
    return render(request, 'add.html', context)


