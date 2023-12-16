from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection


#gets the role of the given user from the database
def get_role(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT role_ID FROM User_tbl \
                    WHERE django_ID = %s",[id])
    
    return cursor.fetchone()[0]

@login_required(login_url='/users/login_user')
def dashboard_view(request, *args, **kwargs):
    #only let admiin view the dasboard
    if get_role(request.user.id) != 3:
        return redirect('/schedule')
        
    return render(request, 'dashboard.html')

