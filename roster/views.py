from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_booker_id(django_id):
    #Connect to the database
    cursor = connection.cursor()
    
    #get performer id from the django ID
    cursor.execute("SELECT booker_ID \
                    FROM Booker NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[django_id])
    
    return cursor.fetchone()[0]


#gets the role of the given user from the database
def get_role(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT role_ID FROM User_tbl \
                    WHERE django_ID = %s",[id])
    
    return cursor.fetchone()[0]

@login_required(login_url='/users/login_user')
def roster_view(request, *args, **kwargs):
    #don't let performers view the roster
    if get_role(request.user.id) == 1:
        return redirect('/schedule')
    
    #get booker id
    booker_id = get_booker_id(request.user.id)
    
    #Connect to the database
    cursor = connection.cursor()
    
    #get the bookers roster from the database
    cursor.execute("SELECT performer_ID, description, rate, displayname, \
                        email, phone_number, genre_type \
                    FROM bookers_roster \
                    WHERE booker_ID = %s",[booker_id])
    
    #wrap the info in a dict to send out for rendering
    context = {'roster':dictfetchall(cursor)}
    
    return render(request, 'roster.html', context)


@login_required(login_url='/users/login_user')
def performer_availability_view(request, id, *args, **kwargs):
    #don't let performers view the roster
    if get_role(request.user.id) == 1:
        return redirect('/schedule')
    
    #get booker id
    booker_id = get_booker_id(request.user.id)
    
    #Connect to the database
    cursor = connection.cursor()
    
    #get the performers  roster from the database
    cursor.execute("SELECT availability_ID, rate, start_time, \
                            end_time, location, displayname \
                    FROM bookers_options \
                    WHERE performer_ID = %s AND \
                            booker_ID = %s",[id, booker_id])
    
    performer_avail = dictfetchall(cursor)
    
    #wrap the info in a dict to send out for rendering
    context = {'obj':performer_avail, 
                'info':performer_avail[0]}
    
    return render(request, 'performeravail.html', context)
