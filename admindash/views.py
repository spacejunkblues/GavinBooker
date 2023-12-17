from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages
from users import views
from django.contrib.auth.models import User

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

#gets the role of the given user from the database
def get_role(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT role_ID FROM User_tbl \
                    WHERE django_ID = %s",[id])
    
    return cursor.fetchone()[0]

@login_required(login_url='/users/login_user')
def userdetail_view(request, r_id, id, *args, **kwargs):
    role_id = get_role(request.user.id)
    #only let admin view the dasboard
    if role_id != 3:
        return redirect('/schedule')
    
    #Connect to the database
    cursor = connection.cursor()
    
    #break out users role
    users_role_id = r_id;
    
    #get performer info
    if users_role_id == 1:
        performer_id = id
        
        #get all performer specific info
        cursor.execute("SELECT django_id, description, rate, displayname, email, phone_number, genre_type, user_type \
                        FROM Performer NATURAL JOIN User_tbl NATURAL JOIN Genre NATURAL JOIN Role \
                        WHERE performer_id = %s", [performer_id])
        #build the context
        info = dictfetchall(cursor)
        
        #Should only return a single row
        if info != []:
            info = info[0]
        
        #get all performers bookings
        cursor.execute("SELECT payment, condition, status_type, start_time, end_time, location, name \
                        FROM Bookings NATURAL JOIN Status \
                            FULL OUTER JOIN Availability ON Availability.availability_id = Bookings.availability_id \
                            LEFT JOIN Booker ON Booker.booker_id = Bookings.booker_id \
                            LEFT JOIN Venue ON Venue.venue_id = Booker.venue_id \
                        WHERE performer_id = %s \
                        ORDER BY start_time", [performer_id])
        #build the context
        tableinfo = dictfetchall(cursor)
        
    #get booker info
    elif users_role_id == 2:
        booker_id = id
        
        #get all booker specific info
        cursor.execute("SELECT django_id, displayname, User_tbl.email, User_tbl.phone_number, user_type, name, \
                            Venue.email AS vemail, address, Venue.phone_number as vphone_number \
                        FROM Booker NATURAL JOIN User_tbl NATURAL JOIN Role LEFT JOIN Venue \
                        ON Venue.venue_id = booker.venue_id \
                        WHERE booker_id = %s", [booker_id])
        #build the context
        info = dictfetchall(cursor)
        
        #Should only return a single row
        if info != []:
            info = info[0]
            
        #get the bookers roster from the database
        cursor.execute("SELECT performer_ID, description, rate, displayname, \
                            email, phone_number, genre_type \
                        FROM bookers_roster \
                        WHERE booker_ID = %s",[booker_id])
        #build the context
        tableinfo = dictfetchall(cursor)
    
    #user is admin?! I guess
    else:
        messages.error(request,"User is not a performer or booker")
        return redirect('/')
        
    #build email form
    if request.method == "POST":
        #clicked on Send Activation email
        if request.POST.get('sendemail')!=None:
            #get user object
            user = User.objects.get(pk=info['django_id'])
            
            #send email
            views.sendActivateEmail(request, user, info['email'], info['displayname'])
            
            #send message to admin
            messages.success(request,"Confirmation email was sent to the user's email on file")
        
    return render(request, 'userdetail.html', {'obj':tableinfo,'role_id':users_role_id, 'info':info})

@login_required(login_url='/users/login_user')
def dashboard_view(request, *args, **kwargs):
    #only let admin view the dasboard
    if get_role(request.user.id) != 3:
        return redirect('/schedule')

    #Connect to the database
    cursor = connection.cursor()
    
    #get all user info
    cursor.execute("SELECT User_tbl.role_id, user_type, booker_id, performer_id, displayname, User_tbl.email, phone_number, \
                        name, rate, genre_type, last_login, is_active, date_joined \
                    FROM User_tbl LEFT JOIN (SELECT user_id, booker_id, name \
                                            FROM Booker LEFT JOIN Venue \
                                            ON Booker.venue_id = Venue.venue_id) as B ON B.user_id = User_tbl.user_id \
                                LEFT JOIN (SELECT user_id, performer_id, rate, genre_type \
                                            FROM Performer LEFT JOIN Genre \
                                            ON Performer.genre_id = Genre.genre_id) as P ON P.user_id = User_tbl.user_id \
                                LEFT JOIN Role ON Role.role_id = User_tbl.role_id \
                                JOIN auth_user ON User_tbl.django_id = auth_user.id \
                    ORDER BY date_joined DESC NULLS LAST")

    #build the context
    info = dictfetchall(cursor)
    
    return render(request, 'dashboard.html', {'obj':info})

