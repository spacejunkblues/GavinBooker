from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from . forms import AddPerformerForm, InvitePerformerForm
from django.contrib import messages
from metrics.loghelper import log_visit
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

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
    
#helper function that loads data into choice fields and formats labels
#helps the roster_view function
def load_performer_form(info_form):
    #get list from database
    cursor = connection.cursor()
    cursor.execute("SELECT performer_id, displayname \
                    FROM Performer INNER JOIN User_tbl \
                    ON Performer.user_id = User_tbl.user_id")

    #reformat result to work in choicefield
    performer_list=[x for x in cursor.fetchall()]

    #store in the Genre choice field
    info_form.fields['performers'].choices=performer_list
    return
    
@login_required(login_url='/users/login_user')
def invite_view(request, *args, **kwargs):
    #only let bookers view the roster
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
        
    if request.method == "POST":
        form = InvitePerformerForm(request.POST)
        
        if form.is_valid():
            #get performer email
            email = form.cleaned_data['email']
            
            #get database connection
            cursor = connection.cursor()
            
            #get Venue's name
            cursor.execute("WITH bookerinfo AS \
                                (SELECT id, user_id, django_id, booker_id, venue_id \
                                FROM auth_user JOIN User_tbl NATURAL JOIN Booker \
                                ON User_tbl.django_ID = auth_user.ID \
                                WHERE auth_user.id = %s) \
                            SELECT name \
                            FROM bookerinfo NATURAL JOIN Venue", 
                            [request.user.id])
            venue=cursor.fetchone()[0]
            
            #check to make sure the email isn't already on the list
            cursor.execute("SELECT COUNT(*) \
                            FROM User_tbl \
                            WHERE email = %s", 
                            [email])
                 
            #let book know to check the drop down menu
            if cursor.fetchone()[0] > 0:
                messages.error(request, ("Performer already has an account. Check the drop down menu."))
            else:
                #email is not in the system, send the invite
                #setup email  
                subject = "Gavin Booking Invitation"
                message = render_to_string('invite_email.html',
                                {'venue': venue,
                                'domain': get_current_site(request).domain})
        
                #email the performer an invintation
                send_mail(
                    subject, #subject
                    message, #message
                    "gavinbooking@gmail.com", #from email
                    [email], #to email
                    fail_silently=False,)
                
                #tell booker that email was sent
                messages.success(request, ("Invitation successfully sent to the performer!"))
            
            #send booker back to the roster
            return redirect('/roster')
    else:
        form = InvitePerformerForm()
    return render(request, 'invite.html', {'form':form})

@login_required(login_url='/users/login_user')
def delete_view(request, id, *args, **kwargs):
    #only let bookers view the roster
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
        
    #get the ids
    performer_id = id
    django_id = request.user.id
    
    #Connect to the database
    cursor = connection.cursor()   
    
    #check that the performer is on the roster
    cursor.execute("SELECT booker_id \
                    FROM Booker NATURAL JOIN User_tbl NATURAL JOIN Roster \
                    WHERE django_id = %s AND performer_id = %s", 
                [django_id, performer_id])                 
    #get query result
    result = cursor.fetchone()
    
    #delete performer from booker's roster
    if result != None:
        #get booker_id
        booker_id=result[0]
        
        #delete performer
        cursor.execute("DELETE FROM Roster \
                        WHERE booker_id = %s AND performer_id = %s", 
                        [booker_id, performer_id])   

    return redirect('/roster')

@login_required(login_url='/users/login_user')
def roster_view(request, *args, **kwargs):
    #only bookers can view the roster
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
        
    #log the visit
    log_visit(request.user.id,"Roster", None)
    
    #get booker id
    booker_id = get_booker_id(request.user.id)
    
    #Connect to the database
    cursor = connection.cursor()
    
    #check to see if the add button was pressed and it wasn't one of the 'Del' buttons
    if request.method == "POST":
        info_form = AddPerformerForm(request.POST)
        
        #format performer form
        load_performer_form(info_form)
        
        #Data is valid (data types are correct)
        if info_form.is_valid():
            #get performer_id
            performer_id = info_form.cleaned_data['performers']
            
            #make sure peformer isn't already added            
            #get names from database
            cursor.execute("SELECT COUNT(*) \
                            FROM Roster \
                            WHERE booker_ID = %s AND performer_ID = %s", 
                            [booker_id, performer_id])
                            
            #check to see if name taken
            if cursor.fetchone()[0] > 0:
                messages.error(request, ("Performer already added to the roster."))
            else:
                #add performer to the roster
                cursor.execute("INSERT INTO Roster  \
                                VALUES (%s, %s);",
                                [booker_id, performer_id])
    else:
        #This else handles initail vist to page (ie, Get request)
        info_form = AddPerformerForm() 

        #format performer form
        load_performer_form(info_form)
    
    #get the bookers roster from the database
    cursor.execute("SELECT performer_ID, description, rate, displayname, \
                        email, phone_number, genre_type \
                    FROM bookers_roster \
                    WHERE booker_ID = %s",[booker_id])
    
    #wrap the info in a dict to send out for rendering
    context = {'roster':dictfetchall(cursor), 'form':info_form}
    
    return render(request, 'roster.html', context)


@login_required(login_url='/users/login_user')
def performer_availability_view(request, id, *args, **kwargs):
    #only let bookers view the roster
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
    
    #log the visit
    log_visit(request.user.id,"RosterPerformer", id)
    
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
    
    #performer is not on the bookers roster
    if performer_avail==[]:
        return redirect('/schedule')
    
    #wrap the info in a dict to send out for rendering
    context = {'obj':performer_avail, 
                'info':performer_avail[0]}
    
    return render(request, 'performeravail.html', context)
