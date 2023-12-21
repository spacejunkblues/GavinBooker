from django.shortcuts import render, redirect
from . forms import ProblemForm
from django.db import connection
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import pandas as pd
from . pandashelper import buildgraph, ConvertMonthtoName, GetBarData
from django.contrib import messages
import math

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
#returns a list. Each list item is a record containing a dictionary
#each dictionary contains the column as the key and the value as the value
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
            
            #build message
            message = render_to_string("problem_email.html",
                                        {'displayname': userData[0]['displayname'],
                                        'username': userData[0]['username'],
                                        'email': userData[0]['email'],
                                        'phone_number': userData[0]['phone_number'],
                                        'severity': severity,
                                        'comment': comment})
                                        
            #send email
            send_mail(
                subject, #subject
                message, #message
                "gavinbooking@gmail.com", #from email
                ["gavinbooking@gmail.com", "kaitlinmbennett@gmail.com"], #to email
                fail_silently=False,)
            
            return redirect('/review/thanks')
    else:
        form = ProblemForm(initial={'severity':'2'})

    #turn wrap the problem form in a dict to be sent for rendering
    context = {'form':form}
    
    return render(request, 'report_problem.html',context)

@login_required(login_url='/users/login_user')
def profilestatus_view(request, year = '', month = '', *args, **kwargs):
    #only let admin view the dasboard
    if get_role(request.user.id) != 3:
        return redirect('/schedule')
    
    #get info from the metric bar, such as current and next month
    #pass current page to enable next and previous
    bar = GetBarData('metrics/profile', year, month)

    #get connection from database
    cursor = connection.cursor()
    
    #get user data
    cursor.execute("SELECT displayname, last_login, is_active, date_joined, user_type \
                    FROM User_tbl INNER JOIN auth_user ON User_tbl.django_id = auth_user.id \
                                    NATURAL JOIN Role")
    cols = [col[0] for col in cursor.description]
    result=cursor.fetchall()
    
    #create DataFrame
    user_df = pd.DataFrame(result,columns=cols)
    roles = user_df['user_type'].unique()
    
    #get all performers not on a roster STORE THIS DATA
    cursor.execute("SELECT genre_id, displayname, user_type \
                    FROM Roster FULL OUTER JOIN Performer ON Roster.performer_id = Performer.performer_id \
                            NATURAL JOIN User_tbl NATURAL JOIN Role \
                    WHERE Roster.performer_id IS NULL")
    cols = [col[0] for col in cursor.description]
    result=cursor.fetchall()
    
    #create DataFrame
    sad_df = pd.DataFrame(result,columns=cols)
    
    #get number of users                
    users_num = {role:len(user_df[user_df['user_type']==role]) for role in roles}
    users_num['total']= len(user_df)
    
    #break out year and month
    user_df['t_last_login']=user_df['last_login'].fillna('')
    #user_df['t_date_joined']=user_df['date_joined'].apply(lambda x: x[:19])
    #user_df['t_last_login']=user_df['t_last_login'].apply(lambda x: x[:19])
    user_df['join month'] = pd.to_datetime(user_df['date_joined']).dt.month
    user_df['join year'] = pd.to_datetime(user_df['date_joined']).dt.year
    user_df['login month'] = pd.to_datetime(user_df['last_login']).dt.month
    user_df['login year'] = pd.to_datetime(user_df['last_login']).dt.year
    
    #total joined
    joined_role_series=user_df[(user_df['join year']==bar['year']) & (user_df['join month']==bar['month'])].groupby('user_type').agg('count')['date_joined']
    
    #total logged in by role
    logged_role_series=user_df[(user_df['login year']==bar['year']) & (user_df['login month']==bar['month'])] \
        .groupby('user_type').agg('count')['last_login']
    
    #not on a roster
    not_roster_num = len(sad_df)
    sad_names_list = sad_df['displayname'].values
    perform_role = sad_df['user_type'].unique()

    
    cols = ['role','joined','logged','notroster']
    
    info=[{cols[0]:role,
            cols[1]:joined_role_series[role] if role in joined_role_series else 0,
            cols[2]:f'{logged_role_series[role]}/{users_num[role]} ({logged_role_series[role]/users_num[role]*100:.0f}%)' \
                if role in logged_role_series else 0, 
            cols[3]:f'{not_roster_num} ({not_roster_num/users_num[role]*100:.0f}%)' \
                if role in perform_role else 'N/A' }
        for role in roles]
   
    
    return render(request, 'profilestatus.html',{'bar':bar,
                                            'users_num':users_num,
                                            'info':info,
                                            'sad_names_list':sad_names_list})
    

@login_required(login_url='/users/login_user')
def gigs_view(request, year = '', month = '', *args, **kwargs):
    #only let admin view the dasboard
    if get_role(request.user.id) != 3:
        return redirect('/schedule')
    
    #get info from the metric bar, such as current and next month
    #pass current page to enable next and previous
    bar = GetBarData('metrics/gigs', year, month)

    #get connection from database
    cursor = connection.cursor()
    
    #get data
    cursor.execute("SElECT rating, Performer.performer_id as performer, Booker.booker_id as booker, \
                        Bookings.booking_id as  booking, comment, status_id, payment, condition, start_time, \
                        end_time, location, description, rate, average, Genre.genre_type as genre, name, address, \
                        T.displayname as performerdisplay, User_tbl.displayname as bookerdisplay \
                    FROM Review FULL OUTER JOIN Bookings ON Bookings.booking_id = Review.booking_id \
                                NATURAL JOIN Availability \
                                FULL OUTER JOIN Performer ON Performer.performer_id = Availability.performer_id \
                                LEFT JOIN Gigs ON Performer.performer_id = Gigs.performer_id \
                                INNER JOIN Genre ON Genre.genre_id = Performer.genre_id \
                                FULL OUTER JOIN Booker ON Booker.booker_id = Bookings.booker_id \
                                LEFT JOIN Venue ON Venue.venue_id = Booker.venue_id \
                                LEFT JOIN User_tbl as T ON T.user_id = Performer.user_id \
                                LEFT JOIN User_tbl ON User_tbl.user_id = Booker.user_id \
                    WHERE EXTRACT(MONTH FROM start_time) = %s AND \
                            EXTRACT(YEAR FROM start_time) = %s",[bar['month'],bar['year']])
    cols = [col[0] for col in cursor.description]
    result=cursor.fetchall()
    
    #create DataFrame
    gigs_df = pd.DataFrame(result,columns=cols)
    
    #used for groupby
    gigs_df['avg_gigs']=gigs_df['average'].fillna(0)
    gigs_df['payment']=gigs_df['payment'].astype(float).fillna(0)
    aggdict = {'rating':'mean',
           'performer':'count',
           'booker':'count',
           'booking':'count',
           'payment':'sum',
           'rate':'mean',
           'average':'mean',
           'avg_gigs':'mean'}
    
    #booked gigs per expected
    try:
        df = gigs_df.groupby('performerdisplay').agg(aggdict)['booking'] - \
            gigs_df.groupby('performerdisplay').agg(aggdict)['avg_gigs']
        ax = df.plot(kind='hist')
        booking_ratio_graph = buildgraph(ax,xlabel='',title="Booked Gigs to Expected Gigs Ratio (high is good)")
    except:
        booking_ratio_graph = ''
        messages.error(request,"no data for Booked Gigs Ratio")
    
    #Gigs booked at Venue
    try:
        ax = gigs_df.groupby('name').agg(aggdict).sort_values('booking',ascending=False)['booking'].head().plot(kind='bar')
        gigs_per_venue_graph = buildgraph(ax,xlabel='',title="Gigs Booked per Venue (top 5)")
    except:
        gigs_per_venue_graph = ''
        messages.error(request,"no data for Gigs Booked per Venue")
        
    #Gigs booked at Venue
    try:
        ax = gigs_df.groupby('name').agg(aggdict).sort_values('booking')['booking'].head().plot(kind='bar')
        gigs_per_venue_bottom_graph = buildgraph(ax,xlabel='',title="Gigs Booked per Venue (bottom 5)")
    except:
        gigs_per_venue_bottom_graph = ''
        messages.error(request,"no data for Gigs Booked per Venue")
    
    #Revenue per Genre
    try:
        ax = gigs_df.groupby('genre').agg(aggdict)['payment'].plot(kind='bar')
        revenue_per_genre_graph = buildgraph(ax,xlabel='',title="Revenue Per Genre")
    except:
        revenue_per_genre_graph = ''
        messages.error(request,"no data for Revenue Per Genre")
    
    #get Revenue per Venue
    try:
        ax = gigs_df.groupby('name').agg(aggdict)['payment'].plot(kind='bar')
        revenue_per_venue_graph = buildgraph(ax,xlabel='',title="Revenue Per Venue")
    except:
        revenue_per_venue_graph = ''
        messages.error(request,"no data for Revenue Per Venue")
        
    #get total gigs
    try:
        total_gigs=gigs_df['booking'].sum()
    except:
        total_gigs = ''
        messages.error(request,"no data for Total Gigs")
        
    #table of Venue bookings and payments
    try:
        venue_bookings_table = gigs_df.to_dict('records')
    except:
        venue_bookings_table = ''
        messages.error(request,"no data for Venue Gigs Table")
    
    return render(request, 'gigs.html',{'bar':bar,
                                            'booking_ratio_graph':booking_ratio_graph,
                                            'gigs_per_venue_graph':gigs_per_venue_graph,
                                            'gigs_per_venue_bottom_graph':gigs_per_venue_bottom_graph,
                                            'revenue_per_genre_graph':revenue_per_genre_graph,
                                            'revenue_per_venue_graph':revenue_per_venue_graph,
                                            'total_gigs':total_gigs,
                                            'venue_bookings_table':venue_bookings_table})

#this will be the main data dump page for admins
#----Site Visited
@login_required(login_url='/users/login_user')
def metric_view(request, year = '', month = '', *args, **kwargs):
    #only let admin view the dasboard
    if get_role(request.user.id) != 3:
        return redirect('/schedule')
    
    #get info from the metric bar, such as current and next month
    #pass current page to enable next and previous
    bar = GetBarData('metrics', year, month)

    #get connection from database
    cursor = connection.cursor()
    
    #get data
    cursor.execute("SELECT * \
                    FROM Visits FULL OUTER JOIN User_tbl ON Visits.user_id = User_tbl.user_id \
                                LEFT JOIN auth_user ON auth_user.id = User_tbl.django_id \
                    WHERE EXTRACT(MONTH FROM date_visited) = %s AND \
                        EXTRACT(YEAR FROM date_visited) = %s \
                    ORDER BY date_visited DESC NULLS LAST",[bar['month'],bar['year']])
    cols = [col[0] for col in cursor.description]
    result=cursor.fetchall()
    
    #create DataFrame
    visits_df = pd.DataFrame(result,columns=cols)
    
    #'remove pointless columns'
    col=["username",
          "page",
          "times_visited",
          "date_visited",
          "role_id",
          "displayname",
          "last_login",
          "is_active",
          "is_staff",
          "date_joined"]
    visits_df = visits_df[col]
    
    #break out year and month
    visits_df['month'] = pd.to_datetime(visits_df['date_visited']).dt.month
    visits_df['year'] = pd.to_datetime(visits_df['date_visited']).dt.year
    
    #used for groupby
    visitagg={'times_visited':'sum','role_id':'mean'}
    
    #visits per page
    try:
        ax = visits_df.groupby(['year','month','page']).agg(visitagg).plot(kind='bar',y='times_visited')
        visits_per_page_graph = buildgraph(ax,xlabel='',title="Visits Per Page")
    except:
        visits_per_page_graph = ''
        messages.error(request,"no data for Visits Per Page")
    
    #visits per user
    try:
        ax = visits_df.groupby(['displayname']).agg(visitagg).sort_values('times_visited', ascending=False).head().plot(kind='bar',y='times_visited')
        top_user_visits_graph = buildgraph(ax,xlabel='',title="Visits Per User (top 5)")
    except:
        top_user_visits_graph = ''
        messages.error(request,"no data for Visits Per User (top 5)")
    
    #visits per role
    try:
        ax = visits_df.groupby(['year','month','role_id']).agg(visitagg).plot(kind='bar',y='times_visited')
        visits_per_role_graph = buildgraph(ax,xlabel=' Performer = 1, Booker = 2, Admin = 3',title="Visits Per Role")
    except:
        visits_per_role_graph = ''
        messages.error(request,"no data for Visits Per Role")
    
    #get total views
    try:
        total_visits=visits_df.groupby(['year','month']).agg(visitagg)['times_visited'].unique()[0]
    except:
        total_visits = ''
        messages.error(request,"no data for Total Visits")
    
    
    return render(request, 'visited.html',{'bar':bar,
                                            'visits_per_page_graph':visits_per_page_graph,
                                            'top_user_visits_graph':top_user_visits_graph,
                                            'visits_per_role_graph':visits_per_role_graph,
                                            'total_visits':total_visits})
