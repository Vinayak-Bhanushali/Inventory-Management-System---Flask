import sqlite3 as sql


conn = sql.connect('database.db')
print ("Opened database successfully")

conn.execute('CREATE TABLE products (productID INTEGER PRIMARY KEY, productName TEXT)')
print ("Table products created successfully")

conn.execute('CREATE TABLE location (locationID INTEGER PRIMARY KEY, locationName TEXT)')
print ("Table location created successfully")

conn.execute('CREATE TABLE productmovement (movementID INTEGER PRIMARY KEY, atTime TEXT, from_location TEXT, to_location TEXT, productName TEXT, qty INTEGER)')
print ("Table productmovement created successfully")

conn.execute('CREATE TABLE balance (locationName TEXT, productName TEXT, qty INTEGER,  PRIMARY KEY (locationName, productName))')
print ("Table balance created successfully")

#Dummy Entries
""" conn.execute("INSERT INTO products (productName)VALUES('Pixel 3')")
conn.commit()
conn.execute("INSERT INTO products (productName)VALUES('OnePlus 6T')")
conn.commit()

conn.execute("INSERT INTO location (locationName)VALUES ('Mumbai')")
conn.commit()
conn.execute("INSERT INTO location (locationName)VALUES ('Delhi')")
conn.commit() """

print("Added Dummy Entries")

