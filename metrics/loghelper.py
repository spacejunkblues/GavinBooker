from django.db import connection
from datetime import datetime

#logs how many times a user visits a certain page on a certain day
def log_visit(django_id, page, ref_id):
    #get current date
    current_date=datetime.now().date()
    
    #Connect to the database
    cursor = connection.cursor()
    
    #get user ID from the django ID
    cursor.execute("SELECT user_id \
                    FROM User_tbl \
                    WHERE django_id = %s",[django_id])
    user_id = cursor.fetchone()
    
    #SQL uses different syntax for checking if something is equal to null
    if user_id != None and ref_id != None:
        #check to see if the user already visited this page today
        cursor.execute("SELECT visit_ID FROM Visits \
                        WHERE user_ID = %s AND page = %s AND date_visited = %s AND ref_ID = %s",
                        [user_id, page,current_date,ref_id])
    elif user_id != None and ref_id == None:
        #check to see if the user already visited this page today
        cursor.execute("SELECT visit_ID FROM Visits \
                        WHERE user_ID = %s AND page = %s AND date_visited = %s AND ref_ID is null",
                        [user_id, page,current_date])
    elif user_id == None and ref_id != None:
        #check to see if the user already visited this page today
        cursor.execute("SELECT visit_ID FROM Visits \
                        WHERE user_ID is null AND page = %s AND date_visited = %s AND ref_ID = %s",
                        [page,current_date,ref_id])
    else: #both are None
        #check to see if the user already visited this page today
        cursor.execute("SELECT visit_ID FROM Visits \
                        WHERE user_ID is null AND page = %s AND date_visited = %s AND ref_ID is null",
                        [page,current_date])

    result=cursor.fetchone()
    
    #log the visit into the database
    if result == None:
        #insert new record
        cursor.execute("INSERT INTO Visits  \
                        VALUES (DEFAULT, %s, %s, %s, %s, %s);",
                        [user_id, page, 1, current_date, ref_id])
    else:
        #get visit_id from result
        visit_id=result[0]
        
        #update the new count into the Visits table
        cursor.execute("UPDATE Visits \
                        SET times_visited = times_visited + 1 \
                        WHERE visit_id = %s",
                        [visit_id])