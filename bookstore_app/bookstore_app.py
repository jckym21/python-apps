#!/usr/bin/env python
# coding: utf-8

# ### Book Store Record Application

# This database application stores book records with title, author,
# year and ISBN information. Each record in the database is unique based on all four fields (i.e. No duplication of records is allowed. However, record with the same title, author and ISBN but different year is allowed. Record adding and updating checks for record dupcation first before record is added or updated. The Graphical User Interface provides users multiple functions including:
#    - Displaying all records
#    - Adding records with search for record duplicates first
#    - Deleting selected records
#    - Updating selected records with search for record duplicates first
#    - Searching records with any one or more of the four record fields
#    - Status bar displaying status of adding, deleting and updating records
# <br>   
# <img src="bookstore_app_snap.png" width = 70%>

# In[1]:


from tkinter import *
import sqlite3


# In[2]:


db_file = "mybooks.db"


# In[3]:


#Create/Connect to database file
def create_table():
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS book_records (title TEXT, author TEXT, year INTEGER, isbn TEXT)")
    conn.commit()
    conn.close()

#Insert record into database
def insert(title, author, year, isbn):
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    cur.execute("INSERT INTO book_records VALUES(?,?,?,?)",(title, author, int(year), isbn))
    conn.commit()
    conn.close()

#Remove record from database
def delete(title, author, year, isbn):
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    cur.execute("DELETE FROM book_records WHERE title=? AND author=? AND year=? AND isbn=?",(title, author, year, isbn))
    conn.commit()
    conn.close()

#Update record from database
def update(title, author, year, isbn, current_title, current_author, current_year, current_isbn):
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    cur.execute("UPDATE book_records SET title=?, author=?, year=?, isbn=? WHERE title=? AND author=? AND year=? AND isbn=?",(title, author, year, isbn, current_title, current_author, current_year, current_isbn))
    conn.commit()
    conn.close()

#Retrieve all records from database
def view():
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    cur.execute("SELECT * FROM book_records")
    rows=cur.fetchall()
    conn.close()
    return rows

#Search record from database
def search(title, author, year, isbn):
    conn=sqlite3.connect(db_file)
    cur=conn.cursor()
    
    command = "SELECT * FROM book_records"
    col = ["title", "author", "year", "isbn"]
    parameter = [title, author, year, isbn]
    command_p = []
    first_para = True
    
    if not all (field=="" for field in parameter):   #SAME AS if not all([title=="", author=="", year=="", isbn==""]):
        command = command + " WHERE"
        for idx, value in enumerate (parameter):
            if value!="":
                if first_para == False: 
                    command = command + " AND"
                command = command + " " + col[idx] + "=?"
                command_p.append(value)
                first_para = False                

    cur.execute(command,command_p)
    rows=cur.fetchall()
    conn.close()
    return rows


# In[4]:


#View all records in database and display it on the GUI
def view_records():
    for idx in reversed(range(t1.size())):        #Same as t1.delete(0.END)
        t1.delete(idx)                             
    for idx, book in enumerate (view(), start=1):
        t1.insert(idx, " [" + str(idx) + "] " + book[0] + ", " + book[1] + ", " + str(book[2]) + ", " + book[3] + "\n")
    status.set("")

#Add record into the datbase with info entered from the GUI.
#Record can only be added if it does not exist in database and 
#all record fields provided are non-empty.
def add_records():
    title_str = str(title.get())
    author_str = str(author.get())
    year_str = str(year.get())
    isbn_str = str(isbn.get())

    if not any([title_str=="", author_str=="", isbn_str=="", year_str==""]):
        current_record = search(title_str, author_str, year_str, isbn_str)
        if len(current_record) == 0:
            insert(title_str, author_str, year_str, isbn_str)
            all_record = True
            view_records()
            status.set("Record added successfully.")
        else:
            status.set("Record already exists.")
    else:
        status.set("One or more field is mssing. Unable to add record.")

#Update record selected in the GUI. Name is used to retreive record from
#database and enterd author, year and ISBN info are updated in the database.
def update_records():
    title_str = str(title.get())
    author_str = str(author.get())
    year_str = str(year.get())
    isbn_str = str(isbn.get())
    
    if not any([title_str=="", author_str=="", isbn_str=="", year_str==""]):
        new_record = search(title_str, author_str, year_str, isbn_str)
        if len(new_record) == 0:
            idx = t1.curselection()[0]  #Index of selection
            current_record = t1.get(idx)
            current_record = current_record.strip('\n')
            current_record = current_record.split("] ", 1)
            current_record = current_record[1].split(", ", 3)
            
            update(title_str, author_str, year_str, isbn_str, 
                   current_record[0], current_record[1], 
                   current_record[2], current_record[3])
            all_record = True
            view_records()
            status.set("Record updated successfully.")
        else:
            status.set("Record exists already. Record is not updated.")

#Remove record selected in the GUI from the database. 
def delete_records():
    title_str = str(title.get())
    author_str = str(author.get())
    year_str = str(year.get())
    isbn_str = str(isbn.get())
    
    delete(title_str, author_str, year_str, isbn_str)
    all_record = True
    view_records()
    status.set("Record deleted successfully.")

#Search record from the database that matches with title, author, 
#year and ISBN info entered in the GUI. Any one or more field 
#can be used for the search.
def search_records():
    title_str = str(title.get())
    author_str = str(author.get())
    year_str = str(year.get())
    isbn_str = str(isbn.get())
    rows = search(title_str, author_str, year_str, isbn_str)

    for idx in reversed(range(t1.size())):
        t1.delete(idx)
    for idx, book in enumerate (rows, start=1):
        t1.insert(idx, " [" + str(idx) + "] " + book[0] + ", " + book[1] + ", " + str(book[2]) + ", " + book[3] + "\n")
    status.set("")

#Callback function to display record details user selected in the listbox.
def callback(event):
    selection = event.widget.curselection()
    if selection:
        idx = selection[0]
        book = t1.get(idx)
        book = book.strip('\n')
        book = book.split("] ", 1)
        book = book[1].split(", ", 3)
        
        title.set(book[0])
        author.set(book[1])
        year.set(book[2])
        isbn.set(book[3])


# In[5]:


#GUI
root = Tk()
root.title("Book Record Database")

l1 = Label(root, text="Title")  #Title label
l1.grid(row=0, column=0)

l2 = Label(root, text="Author") #Author Label
l2.grid(row=0, column=2)

l3 = Label(root, text="Year")   #Year Label
l3.grid(row=1, column=0)

l4 = Label(root, text="ISBN")   #ISBN label
l4.grid(row=1, column=2)

title = StringVar()
e1 = Entry(root, textvariable=title)    #Title entry box
e1.grid(row=0, column=1)

author = StringVar()
e2 = Entry(root, textvariable=author)   #Author entry box
e2.grid(row=0, column=3)

year = StringVar()
e3 = Entry(root, textvariable=year)     #Year entry box
e3.grid(row=1, column=1)

isbn = StringVar()
e4 = Entry(root, textvariable=isbn)     #ISBN entry box
e4.grid(row=1, column=3)

scrollbar = Scrollbar(root)             #Scroll bar for record listbox
scrollbar.grid(row=2, column=4, rowspan=4, sticky='ns')

#Record listbox
t1 = Listbox(root, height=7, width=55, yscrollcommand = scrollbar.set)
t1.grid(row=2, column=0, rowspan=4, columnspan=4)
scrollbar.config(command = t1.yview) 
t1.bind("<<ListboxSelect>>", callback)

#View all record button
b1 = Button(root, text="View All", width=12, command=view_records)
b1.grid(row=0, column=5)

#Search record button
b2 = Button(root, text="Search Entry", width=12, command=search_records)
b2.grid(row=1, column=5)

#Add entry button
b3 = Button(root, text="Add Entry", width=12, command=add_records)
b3.grid(row=2, column=5)

#Update record button
b4 = Button(root, text="Update Selected", width=12, command=update_records)
b4.grid(row=3, column=5)

#Delete record button
b5 = Button(root, text="Delete Selected", width=12, command=delete_records)
b5.grid(row=4, column=5)

#Close application button
b6 = Button(root, text="Close", width=12, command=root.destroy)
b6.grid(row=5, column=5)

status = StringVar()
l5 = Label(root, textvariable=status)    #Status Label
l5.grid(row=6, column=0, columnspan=4)

#Connect/create record table
create_table()

root.mainloop()


# In[6]:


#Sample table and records for testing

#create_table()
#insert("Pete the Cat: Super Pete", "James Dean", 2020, "978-0062868503")
#insert("Pete the Cat and His Four Groovy Buttons", "Eric Litwin", 2012, "0062110586")
#insert("Pete the Cat: The Wheels on the Bus", "James Dean", 2015, "978-0062358523")
#insert("Test1", "JTest", 2000, "84750373")
#insert("Test2", "JTest", 2000, "84940374")
#insert("Test3", "JTest", 1999, "12441222")

#for row in view():
#    print(row)

