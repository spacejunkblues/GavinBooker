from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from metrics.loghelper import log_visit
from . forms import CreateVenueForm

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

#helper function
def get_booker_id(django_id):
    #Connect to the database
    cursor = connection.cursor()
    
    #get booker id from the django ID
    cursor.execute("SELECT booker_ID \
                    FROM Booker NATURAL JOIN User_tbl \
                    WHERE django_ID = %s;",[django_id])
    
    return cursor.fetchone()[0]

@login_required(login_url='/users/login_user')
def createvenue_view(request, *args, **kwargs):
    #only let bookers view the venue page
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
    
    #log the visit
    log_visit(request.user.id,"CreateVenue", None)
	
	#handle submit button
    if request.method == "POST":
	    #get form data
        venue_form = CreateVenueForm(request.POST)
		
	    #Data is valid (data types are correct)
        if venue_form.is_valid():
	
	        #get booker id
            booker_id = get_booker_id(request.user.id)
    
            #Connect to the database
            cursor = connection.cursor()
			
			#create the venue
            cursor.execute("INSERT INTO Venue (venue_ID, booker_ID, name, email, address, phone_number) \
                            VALUES (DEFAULT, %s, %s, %s, %s, %s);",
                                        [booker_id,
                                        venue_form.cleaned_data['venuename'],
                                        venue_form.cleaned_data['venueemail'],
                                        venue_form.cleaned_data['venueaddress'],
                                        venue_form.cleaned_data['venuephone']])
			
			#check to see if this is the first venue added
            cursor.execute("SELECT COUNT(*) \
                            FROM ActiveVenue \
                            WHERE booker_id = %s",
                                        [booker_id])
										
			#make the newly added venue active if there are no active venues currently
            if cursor.fetchone()[0] == 0:
				#get venue_id
                cursor.execute("SELECT venue_id \
                                FROM Venue \
                                WHERE name = %s",[venue_form.cleaned_data['venuename']])
                venue_id = cursor.fetchone()
					
				#make the venue active
                cursor.execute("INSERT INTO ActiveVenue (booker_ID, venue_ID) \
                                VALUES (%s, %s);", [booker_id, venue_id])
									
            return redirect('/venue')
	#load page on first visit, end POST
    else:
        venue_form = CreateVenueForm()

    return render(request, 'createvenue.html', {'form':venue_form})
								

@login_required(login_url='/users/login_user')
def activatevenue_view(request, id, *args, **kwargs):
    #only let bookers view the venue page
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
    
	#get booker id
    booker_id = get_booker_id(request.user.id)
    
    #Connect to the database
    cursor = connection.cursor()
	
	#get the Venues ownded by the booker
    cursor.execute("SELECT venue_id as id \
                    FROM Venue \
                    WHERE booker_ID = %s",[booker_id])
    venues = [row[0] for row in cursor.fetchall()]
	
	#get the Venues shared to the booker
    cursor.execute("SELECT venue_id as id \
                    FROM SharedVenues \
                    WHERE booker_ID = %s",[booker_id])
    other_venues = [row[0] for row in cursor.fetchall()]
	
	#combine the two types of venues into a single list
    venues.extend(other_venues)
	
	#check to see if the ID requested is a venue that the booker has access to
    if id in venues:
		#check to see if this is the first venue added
        cursor.execute("SELECT COUNT(*) \
                        FROM ActiveVenue \
                        WHERE booker_id = %s",
                                    [booker_id])
										
		#There is a Venue that's already active
        if cursor.fetchone()[0] > 0:
			#make the venue active
            cursor.execute("UPDATE ActiveVenue \
                            SET venue_id = %s \
                            WHERE booker_id = %s", [id, booker_id])
		
		#There isn't a venue active yet
        else:
			#make the venue active
            cursor.execute("INSERT INTO ActiveVenue (booker_ID, venue_ID) \
                            VALUES (%s, %s);", [booker_id, venue_id])
		
	

    return redirect('/venue')

								
@login_required(login_url='/users/login_user')
def venue_view(request, *args, **kwargs):
    #only let bookers view the venue page
    if get_role(request.user.id) != 2:
        return redirect('/schedule')
    
    #log the visit
    log_visit(request.user.id,"VenuePage", None)
    
	#get booker id
    booker_id = get_booker_id(request.user.id)
    
    #Connect to the database
    cursor = connection.cursor()
	
	#get the Venues ownded by the booker
    cursor.execute("SELECT venue_id as id, name, email, address, phone_number \
                    FROM Venue \
                    WHERE booker_ID = %s",[booker_id])
    owned_venues = dictfetchall(cursor)
	
	#get the Venues shared to the booker
    cursor.execute("SELECT SharedVenues.venue_id as id, name, Venue.email, address, Venue.phone_number, displayname \
                    FROM SharedVenues INNER JOIN Venue ON Venue.venue_ID = SharedVenues.venue_ID \
                                        INNER JOIN Booker ON Booker.booker_ID = Venue.booker_ID \
				                        INNER JOIN User_tbl ON User_tbl.user_ID = Booker.user_ID \
                    WHERE SharedVenues.booker_ID = %s",[booker_id])
    other_venues = dictfetchall(cursor)
	
	#combine the two types of venues into a single list
    owned_venues.extend(other_venues)
	
	#get the Active Venue
    cursor.execute("SELECT ActiveVenue.venue_ID as id, name, email, address, phone_number \
                    FROM ActiveVenue INNER JOIN Venue ON Venue.venue_ID = ActiveVenue.venue_ID \
                    WHERE ActiveVenue.booker_ID = %s",[booker_id])
    active_venue = dictfetchall(cursor)

    if active_venue == []:
        active_venue={'name':'No Active Venue'}
    else:
        active_venue=active_venue[0]

    return render(request, 'venue.html', {'venues':owned_venues,
                                            'active_venue':active_venue})
