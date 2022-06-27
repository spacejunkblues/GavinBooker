from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . forms import LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

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
                messages.success(request, ('There was an error with loging in'))
                
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

def register_view(request, *args, **kwargs):
    #check to see if the submit button was pressed
    if request.method == "POST":
        #initialize the form object
        form = UserCreationForm(request.POST)
        
        #Data is valid (data types are correct)
        if form.is_valid():
            #this will register the user using djangos system
            #form.save() ***Uncomment when register is finished***
            
            #now that the user is registered, we will login
            #break out data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            
            #*** add permission
            
            #query django authication system
            user = authenticate(request, username=username, password=password)
            
            #Valid user, query django login system
            login(request, user)
                
            #User is logged in
            return redirect('/')
                
    else:
        #This else handles initail vist to page (ei, Get request)
        form = UserCreationForm()
    
    #wrap the form in a dict to send out for rendering
    context = {'form':form}
    
    return render(request, 'register.html',context)

#function will update FK in the User_tbl
def update_dummy_id(user_id, django_id):
    #Connect to the database
    cursor = connection.cursor()
    
    #build sql query statment
    insertion_string = "UPDATE User_tbl SET django_ID = %s WHERE user_ID = %s;"
    
    #send update to database
    cursor.execute(insertion_string,[django_id, user_id] )


#this function will load all dummy users into the django database
def register_dummy(request, *args, **kwargs):            
    #query django authication system
    user = authenticate(request, username='nexttswift', password='1qaz')
    
    #make permissions
    content_type = ContentType.objects.get_for_model(User)
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
        user = User.objects.create_user('jackblue',password='c7uubz')
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
        user = User.objects.create_user('steve',password='xtac1t')
        user.user_permissions.add(permission)
        update_dummy_id(30,user.id)
        
        
        #register admins, 
        #'Admin' should already created using createsuperuser, DDL file assumes ID=1
        permission = permission = Permission.objects.get(name='Can Admin')
        user = User.objects.create_user('daisy',password='df1enu')
        user.user_permissions.add(permission)
        update_dummy_id(32,user.id)
        
        return redirect('/admin')

    else:
        #Invalid log in
        messages.success(request, ('Dummies already loaded'))
    
    return redirect('/users')
    
#this function will load all dummy users into the django database
def delete_dummy(request, *args, **kwargs):            
    #query django authication system
    user = authenticate(request, username='nexttswift', password='1qaz')
    
    #check to make sure dummy users aren't already loaded
    if user is not None:
    
        #this will remove all FK contraints
        for i in range(32):
            update_dummy_id(i+1,1)
            
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
        user = User.objects.get(username='jackblue')
        user.delete()
        
        
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
        user = User.objects.get(username='steve')
        user.delete()
        
        
        #delete admin
        user = User.objects.get(username='daisy')
        user.delete()
        
        return redirect('/admin')

    else:
        #Invalid log in
        messages.success(request, ('No Dummies loaded'))
    
    return redirect('/users')