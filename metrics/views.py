from django.shortcuts import render, redirect
from . forms import ProblemForm
from django.db import connection
from django.core.mail import send_mail

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
#returns a list. Each list item is a record containing a dictionary
#each dictionary contains the column as the key and the value as the value
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
#anyone can report a problem.
#concern is not stored in the database, it is sent via email
#this a beta test thing and may be removed or changed afterwards
def report_problem(request, *args, **kwargs):

    #init the form as defined in forms.py
    if request.method == "POST":
        form = ProblemForm(request.POST)
        #Data is good to email
        if form.is_valid():
            #break out form data
            subject = form.cleaned_data['subject']
            severity = form.cleaned_data['severity']
            comment = form.cleaned_data['comment']
            
            #get connection from database
            cursor = connection.cursor()
                
            #get user ID from the django ID
            cursor.execute("SELECT user_id \
                            FROM User_tbl \
                            WHERE django_id = %s",[request.user.id])
            user_id = cursor.fetchone()
            
            #init data used to send the email incase the user isn't logged on
            userData = [{'displayname':'Anon', 'email':'Anon','phone_number':'Anon', 'username':'Anon'}]
    
            #if there is a user_id then the report is from a logged in user
            if user_id != None:
                #get username
                cursor.execute("SELECT displayname, User_tbl.email, phone_number, username \
                                FROM User_tbl JOIN auth_user \
                                ON User_tbl.django_id = auth_user.id \
                                WHERE User_tbl.user_id = %s",
                                [user_id])
                #formats as a dict in a list aka   [{'fieldname':'value', 'username':'greg'}]
                userData=dictfetchall(cursor)
            
            #send email
            send_mail(
                "Subject here", #subject
                "Here is the message.", #message
                "from@example.com", #from email
                ["spacejunkblues@gmail.com"], #to email
                fail_silently=False,)
                
            print("-----------------")
            print(userData[0]['displayname'])
            print(userData[0]['email'])
            print(userData[0]['phone_number'])
            print(userData[0]['username'])
            print("-----------------")
            
            return redirect('/review/thanks')
    else:
        form = ProblemForm(initial={'severity':'2'})

    #turn wrap the problem form in a dict to be sent for rendering
    context = {'form':form}
    
    return render(request, 'report_problem.html',context)

#this will be the main data dump page for admins
def metric_view(request, *args, **kwargs):
    return render(request, 'review.html', context)
