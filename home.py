from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
app = Flask(__name__)

#db connection
con = sql.connect("database.db",check_same_thread=False)
con.row_factory = sql.Row
cur = con.cursor()

# Dynamic Functions
def getData(tableName,locationName,productName):
   if locationName is None and productName is None:
      queryData = cur.execute("SELECT * FROM {}".format(tableName)).fetchall()
   else:
      queryData = cur.execute("SELECT * FROM {} WHERE locationName = ? AND productName = ? ".format(tableName),(locationName,productName)).fetchall()
   return queryData

def insertData(tableName,newData):
   try:
      if tableName == "products":
         cur.execute("INSERT INTO products (productName)VALUES (?)",(newData['productName'],) )
         con.commit()
         msg = "Product Added Successfully"
      if tableName == "location":
         cur.execute("INSERT INTO location (locationName)VALUES (?)",(newData['locationName'],) )
         con.commit()
         msg = "Location Added Successfully"
      if tableName == "productmovement":
         cur.execute("INSERT INTO productmovement (atTime, from_location, to_location, productName, qty)VALUES (?,?,?,?,?)",(newData['atTime'],newData['from_location'],newData['to_location'],newData['productName'],newData['qty']))
         con.commit()
         msg = "Movement Added Successfully"
      if tableName == "balance":
         cur.execute("INSERT INTO balance (locationName, productName, qty)VALUES (?,?,?)",(newData["locationName"],newData["productName"],0))
         con.commit()
         msg = "Entries of balance updated"
      return msg
   except:
      con.rollback()
      msg = "Error in insert operation"
      return msg
       
def updateData(tableName,newData):
   try:
      if tableName == "products":
         cur.execute("UPDATE products SET productName = ? WHERE productID = ?",(newData['NEWProductName'],newData['ProductID']) )
         con.commit()
         msg = "Product Edited Successfully"
      if tableName == "location":
         cur.execute("UPDATE location SET locationName = ? WHERE locationID = ?",(newData['NEWLocationName'],newData['LocationID']) )
         con.commit()
         msg = "Location Edited Successfully"
      if tableName == "productmovement":
         cur.execute("UPDATE productmovement SET qty = ? WHERE movementID = ?",(newData['editedqty'], newData['movementID']))
         con.commit()
         msg = "Movement Edited Successfully"
      if tableName == "balance":
         cur.execute("UPDATE balance SET qty = ?  WHERE locationName = ? AND productName = ?",(newData['qty'],newData['locationName'],newData['productName']) )
         con.commit()
         msg = "Balance Edited Successfully"
      return msg

   except:
      con.rollback()
      msg = "Error in update operation"
      return msg

def deleteData(tableName,id):
   try:
      if tableName == "products":
         cur.execute("DELETE FROM products WHERE productID = ?",(id))
         con.commit()
         msg = "Product Deleted Successfully"
      if tableName == "location":
         cur.execute("DELETE FROM location WHERE locationID = ?",(id))
         con.commit()
         msg = "Location Deleted Successfully"
      if tableName == "productmovement":
         cur.execute("DELETE FROM productmovement WHERE movementID = ?",(id))
         con.commit()
         msg = "Movement Deleted Successfully"
      return msg
   except:
      con.rollback()
      msg = "Error in delete operation"
      return msg  

#function that updates balance table
def movementManager(locationName,productName,qty):
   oldQuantity = 0
   newQuantity = 0

   if locationName !="-":
      balanceRows = getData("balance",locationName,productName)
      
      #update in balance table if entry exists
      if len(balanceRows) != 0:
         for br in balanceRows:
            oldQuantity = int(br["qty"])
         
         newQuantity = oldQuantity + qty
         if(newQuantity < 0):
            status = "Insuffecient Quantity In "+locationName
            
         else:
            newData = {}
            newData['qty'] = newQuantity
            newData['locationName'] = locationName
            newData['productName'] = productName
            updateData("balance",newData)
            status = "Balance Operation Successfull"
   else:
      status = "Balance Operation Successfull"      
   
   return status
      
#redirect to homepage
@app.route('/')
def root():
   return redirect(url_for('home'))

#homepage
@app.route('/home')
def home():
   #initalize empty list
   data = []
   
   productRows = getData("products",locationName = None, productName = None)
   locationRows = getData("location",locationName = None, productName = None)

   for lr in locationRows:
      for pr in productRows:
         balRow = getData("balance",lr["locationName"],pr["productName"])

         if len(balRow) != 0:
            for br in balRow:
               qty = int(br["qty"])

            innerData = {}
            innerData['locationName'] = lr["locationName"]
            innerData['productName'] = pr["productName"]
            innerData['qty'] = qty

            #push dict to array
            data.append(innerData.copy())
   return render_template('home.html', data = data, locationRows = locationRows)

#_______________________________Product Functions_______________________________________

#product management page
@app.route('/productM')
def productM():
   rows = getData("products",locationName = None, productName = None)
   return render_template('productM.html',rows = rows)

#add new product
@app.route('/addProduct',methods = ['POST'])
def addProduct():
   if request.method == 'POST':
      newData = {}
      newData['productName'] = request.form['pm']
      msg = insertData("products",newData)
      return redirect(url_for('productM')+"?msg="+msg)

#edit product
@app.route('/editProduct',methods = ['POST'])
def editProduct():
   if request.method == 'POST':
      newData = {}
      newData['ProductID'] = request.form['ProductID']
      newData['NEWProductName'] = request.form['NEWProductName']
      msg = updateData("products",newData)
      
      return redirect(url_for('productM')+"?msg="+msg)
         
#delete product
@app.route('/deleteProduct/<productID>')
def deleteProduct(productID):
   msg = deleteData("products",productID)
   return redirect(url_for('productM')+"?msg="+msg)
      

#_______________________________Location Functions_______________________________________

#location management page
@app.route('/locationM')
def locationM():
   rows = getData("location",locationName = None, productName = None)
   return render_template('locationM.html',rows = rows)

#add new location
@app.route('/addLocation',methods = ['POST'])
def addLocation():
   if request.method == 'POST':
      newData = {}
      newData['locationName'] = request.form['lm']
      msg = insertData("location",newData)
      return redirect(url_for('locationM')+"?msg="+msg)

#edit location
@app.route('/editLocation',methods = ['POST'])
def editLocation():
   if request.method == 'POST':
      newData = {}
      newData['LocationID'] = request.form['LocationID']
      newData['NEWLocationName'] = request.form['NEWLocationName']
      msg = updateData("location",newData)

      return redirect(url_for('locationM')+"?msg="+msg)

#delete location
@app.route('/deleteLocation/<locationID>')
def deleteLocation(locationID):
   msg = deleteData("location",locationID)
   return redirect(url_for('locationM')+"?msg="+msg)

#_______________________________Movement Functions_______________________________________

#movement management page
@app.route('/movementM')
def movementM():
   rows = getData("productmovement",locationName = None, productName = None)
   productRows = getData("products",locationName = None, productName = None)
   locationRows = getData("location",locationName = None, productName = None)

   #check if all posiblites of entries exists in balance products
   for pr in productRows:
      for lr in locationRows:
         data = getData("balance",locationName=lr["locationName"],productName = pr["productName"])

         if len(data) == 0:
            newData = {}
            newData['locationName'] = lr["locationName"]
            newData['productName'] = pr["productName"]
            newData['qty'] = 0
            insertData("balance",newData)

   return render_template('movementM.html',rows = rows,  productRows =  productRows, locationRows = locationRows)

#add new movement
@app.route('/addMovement',methods = ['POST'])
def addMovement():
   if request.method == 'POST':
      newData = {}

      newData['atTime'] = request.form['atTime']
      newData['from_location'] = request.form['from_location']
      newData['to_location'] = request.form['to_location']
      newData['productName'] = request.form['productName']
      newData['qty'] = int(request.form['qty'])
      
      #reduce from_location
      status1 = movementManager(newData['from_location'], newData['productName'] ,-(newData['qty']))
      #add to_location
      status2 = movementManager(newData['to_location'], newData['productName'] ,(newData['qty']))

      #only add movement if it has quantity left
      if status1 == "Balance Operation Successfull" and status2 == "Balance Operation Successfull" :
         msg = insertData("productmovement",newData)
      else:
         msg = "Insuffecient Quantity In "+newData['from_location']
         
   return redirect(url_for('movementM')+"?msg="+msg)

#add new movement
@app.route('/editMovement',methods = ['POST'])
def editMovement():
  
   if request.method == 'POST':
      from_location = request.form['from_location']
      to_location = request.form['to_location']
      productName = request.form['productName']
      qty = int(request.form['qty'])
      editedqty = int(request.form['editedqty'])

      newData = {}

      newData['movementID'] = request.form['movementID']
      newData['editedqty'] = request.form['editedqty']

      
      #reduce old quantity
      status1 = movementManager(from_location, productName ,qty)
      status2 = movementManager(to_location, productName ,-qty)

      #add new quantity
      status1 = movementManager(from_location, productName ,-editedqty)
      status2 = movementManager(to_location, productName ,editedqty)

      if status1 == "Balance Operation Successfull" and status2 == "Balance Operation Successfull" :
         msg = updateData("productmovement",newData)
      else:

         #reduce new quantity
         status1 = movementManager(from_location, productName ,-editedqty)
         status2 = movementManager(to_location, productName ,-editedqty)

         #add old quantity
         status1 = movementManager(from_location, productName ,-qty)
         status2 = movementManager(to_location, productName ,qty)

         msg = "Insuffecient Quantity In "+from_location
         
   return redirect(url_for('movementM')+"?msg="+msg)

#delete movement
@app.route('/deleteMovement',methods = ['POST'])
def deleteMovement():
   if request.method == 'POST':
      movementID = request.form['movementID']
      from_location = request.form['from_location']
      to_location = request.form['to_location']
      productName = request.form['productName']
      qty = int(request.form['qty'])
      
      #add back to from_location
      status1 = movementManager(from_location, productName ,qty)
      #sub from to_location
      status2 = movementManager(to_location, productName ,-qty)

      #only add movement if it has quantity left
      if status1 == "Balance Operation Successfull" and status2 == "Balance Operation Successfull" :
         msg = deleteData("productmovement",movementID)
      else:
         msg = "Insuffecient Quantity In "+from_location
      return redirect(url_for('movementM')+"?msg="+msg)
   
if __name__ == '__main__':
   app.run(debug = True)
