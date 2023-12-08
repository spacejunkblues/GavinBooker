from django.shortcuts import render, redirect
from django.db import connection
from . forms import ReviewForm
from metrics.loghelper import log_visit

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
    


#this handles calling the page after a review is submitted
def thanks_view(request, *args, **kwargs):
    return render(request, 'thanks.html')
    
#function checks to see if the given booking_id is allowed to be reviewed
def reviewable(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #pull only booked shows from the database
    cursor.execute("SELECT COUNT(*) FROM Bookings \
                    WHERE status_ID = 2 AND \
                        booking_ID = %s",[id])
    return cursor.fetchone()[0] > 0


def review_view(request,id, *args, **kwargs):
    #make sure only valid bookings can be reviewed
    if not reviewable(id):
        return redirect('/review')
        
    #log the visit
    log_visit(request.user.id,"ReviewBooking",id)
    
    #Connect to the database
    cursor = connection.cursor()
    
    #init the form as defined in forms.py
    if request.method == "POST":
        form = ReviewForm(request.POST)
        #Data is good to insert into database
        if form.is_valid():
            #break out data
            new_rating = form.cleaned_data['rating']
            new_comment = form.cleaned_data['comment']
            
            #build query
            insertion_string = "INSERT INTO Review VALUES (DEFAULT, %s, %s, %s);"
            
            #insert new review into database
            cursor.execute(insertion_string,[id, new_rating, new_comment] )
            
            return redirect('../thanks')
    else:
        form = ReviewForm()
    
    #turn wrap the reviews in a dict to be sent for rendering
    context = {'form':form}
    
    
    return render(request, 'submit_review.html', context)
    

#this is the landing page where all shows are displayed
def allbookings_view(request, *args, **kwargs):
    #log the visit
    log_visit(request.user.id,"Review",None)
    
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query for all 'booked' bookings
    cursor.execute("SELECT * FROM reviewers_booked \
                    WHERE status_ID = 2")
   

    #turn wrap the reviews in a dict to be sent for rendering
    context = {'obj':dictfetchall(cursor)}
    
    return render(request, 'review.html', context)

