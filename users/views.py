from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . forms import LoginForm, RegForm, PasswordResetForm, EditForm, PerformerEditForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User, Permission
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from .token import account_activation_token
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail

#fucntion provided by Django documentation
#https://docs.djangoproject.com/en/4.0/topics/db/sql/
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def login_view(request, *args, **kwargs):
    #check to see if the submit button was pressed
    if request.method == "POST":
        #initialize the form object
        form = LoginForm(request.POST)
        
        #Data is valid (data types are correct)
        if form.is_valid():
            #break out data
            username = form.cleaned_data['userName']
            password = form.cleaned_data['password']
            
            #query django authication system
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                #Valid user, query django login system
                login(request, user)
                
                #User is logged in
                return redirect('/')
            else:
                #Invalid log in
                messages.error(request, ('There was an error with loging in'))
                
    else:
        #This else handles initail vist to page (ei, Get request)
        form = LoginForm()
    
    #wrap the form in a dict to send out for rendering
    context = {'form':form}
    
    return render(request, 'login.html',context)


@login_required(login_url='/users/login_user')
def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('/users/login_user')

def reset_view(request, uidb64, token):
    #get the user from the uid
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    #user authiticated via email toke, reset the password the user
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            
            if form.is_valid():
                #update the new password
                form.save()
                
                #change the user back to active so he can log in
                user.is_active = True
                user.save()
                
                #log in user
                login(request, user)
                messages.success(request, ('Password successfully changed!'))
                return redirect('/')
        else:
            form = SetPasswordForm(user)
        
        return render(request, 'passwordreset_newpassword.html', {'form':form})
    else:
        messages.error(request,('link invalid.'))
    return redirect('/')

def passwordreset_view(request, *args, **kwargs):
    #handle post of the form
    if request.method == "POST":
        #initialize the form object
        form = PasswordResetForm(request.POST)
        
        
        #Data is valid (data types are correct)
        if form.is_valid():
            #break out data
            username = form.cleaned_data['userName']
            
            #Connect to the database
            cursor = connection.cursor()
    
            #send a query to get the user's email
            cursor.execute("SELECT User_tbl.email, User_tbl.displayname, auth_user.id \
                            FROM auth_user JOIN User_tbl \
                            ON User_tbl.django_ID = auth_user.ID \
                            WHERE username = %s",[username])
            result = cursor.fetchone()
            
            #username exists
            if result != None:
                (email, displayname, id) = result
            
                #get user object
                user = User.objects.get(pk=id)
                user.is_active = False
                user.save()
                
                #send email    
                subject = "Gavin Booking Password Reset"
                message = render_to_string('passwordreset_email.html',
                                {'user': displayname,
                                'domain': get_current_site(request).domain,
                                'uid':urlsafe_base64_encode(force_bytes(id)),
                                'token':account_activation_token.make_token(user)})
        
                #send the email
                send_mail(
                    subject, #subject
                    message, #message
                    "gavinbooking@gmail.com", #from email
                    [email], #to email
                    fail_silently=False,)
            
            #render to a holding page
            return render(request, 'passwordreset_holding.html')
    else:
        #init form
        form = PasswordResetForm()
        
    #wrap the form in a dict to send out for rendering
    context = {'form':form}
    
    #render password rest form
    return render(request, 'passwordreset.html',context)



#sends an activate email to the user who just registered
def sendActivateEmail(request, user, user_email, displayname):
    subject = "Gavin Booking Account Activation Email"
    message = render_to_string('activate_email.html',
                            {'user': displayname,
                            'domain': get_current_site(request).domain,
                            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                            'token':account_activation_token.make_token(user)})
    
    #send the email
    send_mail(
        subject, #subject
        message, #message
        "gavinbooking@gmail.com", #from email
        [user_email], #to email
        fail_silently=False,)
        

#quick helper function
def get_role(id):
    #Connect to the database
    cursor = connection.cursor()
    
    #send a query to get all availabilities
    cursor.execute("SELECT role_ID FROM User_tbl \
                    WHERE django_ID = %s",[id])
    
    return cursor.fetchone()[0]  

def activate_view(request, uidb64, token):
    #get the user from the uid
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    #user authiticated via email toke, activate the user
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)

        #get the role
        role_id = get_role(user.id)

        #Welcome Message
        if role_id==1:
            messages.success(request, ('Welcome to Gavin Booking! Click on the "Add" buttons below to start showing bookers when you are available!'))
        elif role_id==2:
            messages.success(request, ('Welcome to Gavin Booking! Click on the Scroll button above to start adding performers to your Roster!'))
    else:
        messages.error(request,('Activation link invalid.'))
    return redirect('/')

#helper function that loads data into choice fields
#helps the register_view function
def load_reg_form(info_form):
    #get list from database
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Genre")

    #reformat result to work in choicefield
    genre_list=[x for x in cursor.fetchall()]

    #store in the Genre choice field
    info_form.fields['genre'].choices=genre_list

    return

def register_view(request, *args, **kwargs):
    #check to see if the submit button was pressed
    if request.method == "POST":
        #initialize the form object
        cred_form = UserCreationForm(request.POST)
        info_form = RegForm(request.POST)
        
        #format reg form
        load_reg_form(info_form)
        
        #Data is valid (data types are correct)
        if cred_form.is_valid() and info_form.is_valid():
            #this will register the user using djangos system
            user = cred_form.save(commit=False)
            user.is_active = False
            user.save()
            
            #break out user data
            username = cred_form.cleaned_data['username']
            password = cred_form.cleaned_data['password1']
            if info_form.cleaned_data['role'] == 'perform':
                role_id=1
            elif info_form.cleaned_data['role'] == 'book':
                role_id=2
            else:
                return redirect('/')
            
            #store user "info"
            #get connection from database
            cursor = connection.cursor()
            
            #get django ID from the newly created user
            cursor.execute("SELECT id \
                            FROM auth_user \
                            WHERE username = %s",[username])
            django_id = cursor.fetchone()
            
            #insert fields into base
            cursor.execute("INSERT INTO User_tbl  \
                            VALUES (DEFAULT, %s, %s, %s, %s, %s);",
                                [role_id,
                                django_id,
                                info_form.cleaned_data['displayname'],
                                info_form.cleaned_data['email'],
                                info_form.cleaned_data['phone']])
            
            #get user ID from the newly inserted user_tbl entry
            cursor.execute("SELECT user_id \
                            FROM User_tbl \
                            WHERE django_id = %s",[django_id])
            user_id = cursor.fetchone()
                            
            #insert performer fields into database
            if role_id==1:
                cursor.execute("INSERT INTO Performer  \
                                VALUES (DEFAULT, %s, %s, %s, %s);",
                                    [info_form.cleaned_data['genre'],
                                    user_id,
                                    info_form.cleaned_data['description'],
                                    info_form.cleaned_data['rate']])
                                    
                #get performer ID from the newly inserted entry
                cursor.execute("SELECT performer_id \
                            FROM Performer \
                            WHERE user_id = %s",[user_id])  
                performer_id = cursor.fetchone()
                            
                #log average gigs performed per month. This will only be used in beta testing
                cursor.execute("INSERT INTO Gigs  \
                                VALUES (DEFAULT, %s, %s);",
                                    [performer_id,
                                    info_form.cleaned_data['averagegigs']])

            #insert booker fields into database
            elif role_id==2:  
			    #create record in Booker table
                cursor.execute("INSERT INTO Booker \
                                VALUES (DEFAULT, %s);",
                                    [user_id])      			
                
                #if venue_id is 0, that means a new venue must be created
                if info_form.cleaned_data['venue']=='0':
				    #get booker id
                    cursor.execute("SELECT booker_ID FROM Booker \
                                   WHERE user_ID = %s",[user_id])
                    booker_id = cursor.fetchone()
					
                    #create the venue
                    cursor.execute("INSERT INTO Venue (venue_ID, booker_ID, name, email, address, phone_number) \
                                    VALUES (DEFAULT, %s, %s, %s, %s, %s);",
                                        [booker_id,
                                        info_form.cleaned_data['venuename'],
                                        info_form.cleaned_data['venueemail'],
                                        info_form.cleaned_data['venueaddress'],
                                        info_form.cleaned_data['venuephone']])
                                        
                    #get venue_id
                    cursor.execute("SELECT venue_id \
                                    FROM Venue \
                                    WHERE name = %s",[info_form.cleaned_data['venuename']])
                    venue_id = cursor.fetchone()
            
			        #make this venue active
                    cursor.execute("INSERT INTO ActiveVenue (booker_ID, venue_ID) \
                                    VALUES (%s, %s);", [booker_id, venue_id,])
										
            #set permission based on role
            if role_id==1:
                permission = Permission.objects.get(name='Can Perform')
            elif role_id==2:
                permission = Permission.objects.get(name='Can Book')
                
            #register the user permission
            user.user_permissions.add(permission)
            
            #user is now registered but inactive. user needs to verify email to continue
            sendActivateEmail(request, user, info_form.cleaned_data['email'], info_form.cleaned_data['displayname'])
            
            #Send user to a holding page until their email has been confirmed.
            return render(request, 'registered.html',{'email':info_form.cleaned_data['email']})
                
    else:
        #This else handles initail vist to page (ie, Get request)
        cred_form = UserCreationForm()
        info_form = RegForm(initial={'role':'perform', 'venue':0}) #set default value
        
        #format reg form
        load_reg_form(info_form)
    
    #wrap the form in a dict to send out for rendering
    context = {'cred':cred_form, 'info':info_form}
    
    return render(request, 'register.html',context)

#controls rending the edit landing page
#No URL tied to this, it's called after an update to the edit page
def edit_landing(request, role_id, user_id):	
	#get connection from database
	cursor = connection.cursor()
	
	#get user info for all types of users
	cursor.execute("SELECT role_ID, displayname, User_tbl.email, phone_number, username \
					FROM User_tbl INNER JOIN auth_user ON auth_user.id = User_tbl.django_ID \
					WHERE django_ID = %s",[request.user.id])
	user_info = dictfetchall(cursor)
	
	#if Performer:
	if role_id == 1:
		#get performer specific data
		cursor.execute("SELECT genre_type, description, rate \
						FROM Performer NATURAL JOIN Genre \
						WHERE user_ID = %s",[user_id])
		performer_info = dictfetchall(cursor)
		
		#add to user_info			
		user_info[0].update(performer_info[0])			
	
	return render(request, 'edit_landing.html', {'info':user_info[0]})

#edit users profile
@login_required(login_url='/users/login_user')
def edit_view(request, *args, **kwargs):
	#get role
	role_id = get_role(request.user.id)
	
	#get connection from database
	cursor = connection.cursor()
	
	#get user_id
	cursor.execute("SELECT user_ID FROM User_tbl \
					WHERE django_ID = %s",[request.user.id])
	user_id=cursor.fetchone()[0]  
	
    #check for post
	if request.method == "POST":
		#initialize the form object
		user_form = EditForm(request.POST)
		performer_form = PerformerEditForm(request.POST)
        
        #format reg form
		load_reg_form(performer_form)
        
        #Data is valid (data types are correct)
		if user_form.is_valid() and (performer_form.is_valid() or role_id != 1):
			#update data
			cursor.execute("UPDATE User_tbl \
							SET displayname = %s, \
								phone_number = %s \
							WHERE django_ID = %s",[user_form.cleaned_data['displayname'],
													user_form.cleaned_data['phone'],
													request.user.id])
			
			#update performer info
			if role_id == 1:
				cursor.execute("UPDATE Performer \
								SET genre_id = %s, \
									description = %s, \
									rate = %s \
								WHERE user_ID = %s",[performer_form.cleaned_data['genre'],
														performer_form.cleaned_data['description'],
														performer_form.cleaned_data['rate'],
														user_id])
		else:
			messages.error(request, ('Something went wrong'))
		
		#send user to confirmation page
		return edit_landing(request, role_id, user_id)
	
	#load current data
	else:		
		#get user info for all types of users
		cursor.execute("SELECT role_ID, displayname, User_tbl.email, phone_number, username \
						FROM User_tbl INNER JOIN auth_user ON auth_user.id = User_tbl.django_ID \
						WHERE django_ID = %s",[request.user.id])
		user_info = dictfetchall(cursor)
		
		#make sure there is a user
		if user_info == []:
			return redirect('/')
		
		#if Performer:
		if role_id == 1:
			#get performer specific data
			cursor.execute("SELECT genre_ID, description, rate \
							FROM Performer \
							WHERE user_ID = %s",[user_id])
			performer_info = dictfetchall(cursor)
				
			#make sure there is a performer record
			if performer_info == []:
				return redirect('/')
			
			#add to user_info			
			user_info[0].update(performer_info[0])			

		#shed the list (should only need one row)
		user_info=user_info[0]
		
		#load forms with default data
		user_form = EditForm(initial={'displayname':user_info['displayname'],
										'phone':user_info['phone_number']})

		#load performer info
		if role_id == 1:
			init_dict = {'genre':user_info['genre_id'],
						'description':user_info['description'],
						'rate':user_info['rate']}
		else:
			init_dict ={}
		performer_form = PerformerEditForm(initial=init_dict)
		
		#format reg form
		load_reg_form(performer_form)
		
	#end else for POST

	return render(request, 'edit.html', {'user_form':user_form,
										'performer_form':performer_form,
										'info':user_info})

#function will update FK in the User_tbl
def update_dummy_id(user_id, django_id):
    #Connect to the database
    cursor = connection.cursor()
    
    #build sql query statment
    insertion_string = "UPDATE User_tbl SET django_ID = %s WHERE user_ID = %s;"
    
    #send update to database
    cursor.execute(insertion_string,[django_id, user_id] )


#this function will load all dummy users into the django database
#this function will error out if the permissions are already made
#also, the admin user add will error out if you did "createsuperuser"
def register_dummy(request, *args, **kwargs):            
    #query django authication system
    user = authenticate(request, username='nexttswift', password='1qaz')
    #make permissions
    content_type = ContentType.objects.get_for_model(User)
    
    #I commented these out. But they need to be ran the first time
    Permission.objects.create(codename='can_perform',
                                name='Can Perform',
                                content_type=content_type)
    Permission.objects.create(codename='can_book',
                                name='Can Book',
                                content_type=content_type)
    
    Permission.objects.create(codename='can_admin',
                                name='Can Admin',
                                content_type=content_type)
    
    #check to make sure dummy users aren't already loaded
    if user is None:
        permission = permission = Permission.objects.get(name='Can Perform')
        #register performers
        user = User.objects.create_user('nexttswift',password='1qaz')
        user.user_permissions.add(permission)
        update_dummy_id(1,user.id)
        user = User.objects.create_user('bluesinger',password='2wsx')
        user.user_permissions.add(permission)
        update_dummy_id(2,user.id)
        user = User.objects.create_user('bob',password='3edc')
        user.user_permissions.add(permission)
        update_dummy_id(3,user.id)
        user = User.objects.create_user('onemanband',password='smn01r')
        user.user_permissions.add(permission)
        update_dummy_id(4,user.id)
        user = User.objects.create_user('greesejazz',password='19cr1b')
        user.user_permissions.add(permission)
        update_dummy_id(5,user.id)
        user = User.objects.create_user('notbieber',password='zz46mt')
        user.user_permissions.add(permission)
        update_dummy_id(6,user.id)
        user = User.objects.create_user('betterthanswift',password='gx7wsu')
        user.user_permissions.add(permission)
        update_dummy_id(7,user.id)
        user = User.objects.create_user('allcountry',password='znul5u')
        user.user_permissions.add(permission)
        update_dummy_id(8,user.id)
        user = User.objects.create_user('bigcountry',password='ho50pg')
        user.user_permissions.add(permission)
        update_dummy_id(9,user.id)
        user = User.objects.create_user('mjcovers',password='iq4r3g')
        user.user_permissions.add(permission)
        update_dummy_id(10,user.id)
        user = User.objects.create_user('elvis',password='4lbmp7')
        user.user_permissions.add(permission)
        update_dummy_id(11,user.id)
        user = User.objects.create_user('jonnymoney',password='z6fh9v')
        user.user_permissions.add(permission)
        update_dummy_id(12,user.id)
        user = User.objects.create_user('jftl',password='3clb3t')
        user.user_permissions.add(permission)
        update_dummy_id(13,user.id)
        user = User.objects.create_user('flowercolor',password='6d1li1')
        user.user_permissions.add(permission)
        update_dummy_id(14,user.id)
        user = User.objects.create_user('lessthanswift',password='0m98x7')
        user.user_permissions.add(permission)
        update_dummy_id(15,user.id)
        user = User.objects.create_user('fourmanband',password='q810x3')
        user.user_permissions.add(permission)
        update_dummy_id(16,user.id)
        user = User.objects.create_user('latincovers',password='ac8djc')
        user.user_permissions.add(permission)
        update_dummy_id(17,user.id)
        user = User.objects.create_user('swiftthis',password='7khee7')
        user.user_permissions.add(permission)
        update_dummy_id(18,user.id)
        user = User.objects.create_user('edmislife',password='6qyk0q')
        user.user_permissions.add(permission)
        update_dummy_id(19,user.id)
        user = User.objects.create_user('mags',password='diamond456')
        user.user_permissions.add(permission)
        update_dummy_id(20,user.id)
        
        
        #register bookers
        permission = permission = Permission.objects.get(name='Can Book')
        user = User.objects.create_user('jim',password='1qaz')
        user.user_permissions.add(permission)
        update_dummy_id(21,user.id)
        user = User.objects.create_user('jack',password='166jlv')
        user.user_permissions.add(permission)
        update_dummy_id(22,user.id)
        user = User.objects.create_user('john',password='4idkcy')
        user.user_permissions.add(permission)
        update_dummy_id(23,user.id)
        user = User.objects.create_user('jill',password='2wsx')
        user.user_permissions.add(permission)
        update_dummy_id(24,user.id)
        user = User.objects.create_user('jasmine',password='6td5r8')
        user.user_permissions.add(permission)
        update_dummy_id(25,user.id)
        user = User.objects.create_user('jorge',password='3edc')
        user.user_permissions.add(permission)
        update_dummy_id(26,user.id)
        user = User.objects.create_user('jex',password='f19qgq')
        user.user_permissions.add(permission)
        update_dummy_id(27,user.id)
        user = User.objects.create_user('janet',password='vzps0b')
        user.user_permissions.add(permission)
        update_dummy_id(28,user.id)
        user = User.objects.create_user('james',password='yi0i4w')
        user.user_permissions.add(permission)
        update_dummy_id(29,user.id)
        user = User.objects.create_user('stark',password='diamond456')
        user.user_permissions.add(permission)
        update_dummy_id(30,user.id)
        
        
        #register admins, 
        permission = permission = Permission.objects.get(name='Can Admin')
        user = User.objects.create_user('admin',password='1qaz2wsx!QAZ@WSX')
        user.user_permissions.add(permission)
        update_dummy_id(31,user.id)
        user = User.objects.create_user('daisy',password='df1enu')
        user.user_permissions.add(permission)
        update_dummy_id(32,user.id)
        
        return redirect('/admin')

    else:
        #Invalid log in
        messages.error(request, ('Dummies already loaded'))
    
        
    return redirect('/users')
    
#this function will load all dummy users into the django database
def delete_dummy(request, *args, **kwargs):            
    #query django authication system
    user = authenticate(request, username='nexttswift', password='1qaz')
    
    #check to make sure dummy users aren't already deleted
    if user is not None:
    
        #this will remove all FK contraints
        #for i in range(32):
        #    update_dummy_id(i+1,1)
            
        #delete performers
        user = User.objects.get(username='nexttswift')
        user.delete()
        user = User.objects.get(username='bluesinger')
        user.delete()
        user = User.objects.get(username='bob')
        user.delete()
        user = User.objects.get(username='onemanband')
        user.delete()
        user = User.objects.get(username='greesejazz')
        user.delete()
        user = User.objects.get(username='notbieber')
        user.delete()
        user = User.objects.get(username='betterthanswift')
        user.delete()
        user = User.objects.get(username='allcountry')
        user.delete()
        user = User.objects.get(username='bigcountry')
        user.delete()
        user = User.objects.get(username='mjcovers')
        user.delete()
        user = User.objects.get(username='elvis')
        user.delete()
        user = User.objects.get(username='jonnymoney')
        user.delete()
        user = User.objects.get(username='jftl')
        user.delete()
        user = User.objects.get(username='flowercolor')
        user.delete()
        user = User.objects.get(username='lessthanswift')
        user.delete()
        user = User.objects.get(username='fourmanband')
        user.delete()
        user = User.objects.get(username='latincovers')
        user.delete()
        user = User.objects.get(username='swiftthis')
        user.delete()
        user = User.objects.get(username='edmislife')
        user.delete()
        #user = User.objects.get(username='mags')
        #user.delete()
        
        
        #delete bookers
        user = User.objects.get(username='jim')
        user.delete()
        user = User.objects.get(username='jack')
        user.delete()
        user = User.objects.get(username='john')
        user.delete()
        user = User.objects.get(username='jill')
        user.delete()
        user = User.objects.get(username='jasmine')
        user.delete()
        user = User.objects.get(username='jorge')
        user.delete()
        user = User.objects.get(username='jex')
        user.delete()
        user = User.objects.get(username='janet')
        user.delete()
        user = User.objects.get(username='james')
        user.delete()
        #user = User.objects.get(username='stark')
        #user.delete()
        
        
        #delete admin
        #user = User.objects.get(username='admin')
        #user.delete()
        #user = User.objects.get(username='daisy')
        #user.delete()
        
        return redirect('/admin')

    else:
        #Invalid log in
        messages.error(request, ('No Dummies loaded'))
    
    return redirect('/users')