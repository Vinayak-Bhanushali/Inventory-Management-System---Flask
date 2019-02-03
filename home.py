from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
app = Flask(__name__)

#redirect to homepage
@app.route('/')
def root():
   return redirect(url_for('home'))

#homepage
@app.route('/home')
def home():
   con = sql.connect("database.db")
   con.row_factory = sql.Row

   #initalize empty list
   data = []
   
   cur = con.cursor()

   cur.execute("select * from location")
   locationRows = cur.fetchall()

   cur.execute("select * from products")
   productRows = cur.fetchall()

   for lr in locationRows:
      location = lr["locationName"]
      for pr in productRows:
         product = pr["productName"]

         cur.execute("SELECT qty FROM balance WHERE locationName = ? AND productName = ? ",(location,product))
         balRow = cur.fetchall()

         if len(balRow) != 0:
            for br in balRow:
               qty = int(br["qty"])

            innerData = {}
            innerData['locationName'] = location
            innerData['productName'] = product
            innerData['qty'] = qty

            #push dict to array
            data.append(innerData.copy())
   return render_template('home.html', data = data, locationRows = locationRows)

#_______________________________Product Functions_______________________________________

#product management page
@app.route('/productM')
def productM():

   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from products")
   
   rows = cur.fetchall()

   return render_template('productM.html',rows = rows)

#add new product
@app.route('/addProduct',methods = ['POST'])
def addProduct():
   if request.method == 'POST':
      try:
         productName = request.form['pm']
         
         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO products (productName)VALUES (?)",(productName,) )
            
            con.commit()
            msg = "Product Added Successfully"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         return redirect(url_for('productM')+"?msg="+msg)
         con.close()

#edit product
@app.route('/editProduct',methods = ['POST'])
def editProduct():
   if request.method == 'POST':
      try:
         productID = request.form['ProductID']
         productName = request.form['NEWProductName']
         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE products SET productName = ? WHERE productID = ?",(productName,productID) )
            
            con.commit()
            msg = "Product Edited Successfully"
      except:
         con.rollback()
         msg = "error in update operation"
      
      finally:
         return redirect(url_for('productM')+"?msg="+msg)
         con.close()

#delete product
@app.route('/deleteProduct/<productID>')
def deleteProduct(productID):
   try:
      with sql.connect("database.db") as con:
         cur = con.cursor()
         cur.execute("DELETE FROM products WHERE productID = ?",(productID,))
         
         con.commit()
         msg = "Product Deleted Successfully"
   except:
      con.rollback()
      msg = "error in delete operation"
   
   finally:
      return redirect(url_for('productM')+"?msg="+msg)
      con.close()

#_______________________________Location Functions_______________________________________

#location management page
@app.route('/locationM')
def locationM():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from location")
   
   rows = cur.fetchall()

   return render_template('locationM.html',rows = rows)

#add new location
@app.route('/addLocation',methods = ['POST'])
def addLocation():
   if request.method == 'POST':
      try:
         locationName = request.form['lm']
         
         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO location (locationName)VALUES (?)",(locationName,) )
            
            con.commit()
            msg = "Location successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         return redirect(url_for('locationM')+"?msg="+msg)
         con.close()

#edit location
@app.route('/editLocation',methods = ['POST'])
def editLocation():
   if request.method == 'POST':
      try:
         locationID = request.form['LocationID']
         locationName = request.form['NEWLocationName']
         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("UPDATE location SET locationName = ? WHERE locationID = ?",(locationName,locationID) )
            
            con.commit()
            msg = "Location Edited Successfully"
      except:
         con.rollback()
         msg = "error in update operation"
      
      finally:
         return redirect(url_for('locationM')+"?msg="+msg)
         con.close()

#delete location
@app.route('/deleteLocation/<locationID>')
def deleteLocation(locationID):
   try:
      with sql.connect("database.db") as con:
         cur = con.cursor()
         cur.execute("DELETE FROM location WHERE locationID = ?",(locationID,))
         
         con.commit()
         msg = "Location Deleted Successfully"
   except:
      con.rollback()
      msg = "error in delete operation"
   
   finally:
      return redirect(url_for('locationM')+"?msg="+msg)
      con.close()

#_______________________________Movement Functions_______________________________________

#movement management page
@app.route('/movementM')
def movementM():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from productmovement")
   
   rows = cur.fetchall()

   cur.execute("select * from products")
   productRows = cur.fetchall()

   cur.execute("select * from location")
   locationRows = cur.fetchall()

   #check if all posiblites of entries exists in balance products
   for pr in productRows:
      for lr in locationRows:
         cur.execute("SELECT * FROM balance WHERE locationName = ? AND productName = ? ",(lr["locationName"],pr["productName"]))
         data = cur.fetchall()

         if len(data) == 0:
            cur.execute("INSERT INTO balance (locationName, productName, qty)VALUES (?,?,?)",(lr["locationName"],pr["productName"],0))
            con.commit()
            

   return render_template('movementM.html',rows = rows,  productRows =  productRows, locationRows = locationRows)


def movementManager(from_location,to_location,productName,qty):
   with sql.connect("database.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()

      oldQuantity = 0
      newQuantity = 0
   
      #ignore in case of move in
      if from_location != "-":
         cur.execute("select * from balance WHERE locationName = ? AND productName = ?",(from_location,productName))
         balanceRows = cur.fetchall()
         #update in balance table if entry exists
         if len(balanceRows) != 0:
            for br in balanceRows:
               oldQuantity = int(br["qty"])
            
            newQuantity = oldQuantity - qty
            
            if(newQuantity < 0):
               msg = "Insuffecient Quantity In "+from_location
               return msg
               con.close()


            cur.execute("UPDATE balance SET qty = ?  WHERE locationName = ? AND productName = ?",(newQuantity,from_location,productName) )
            con.commit()

      #ignore in case of move out
      if to_location != "-":
         cur.execute("select * from balance WHERE locationName = ? AND productName = ?",(to_location,productName))
         balanceRows = cur.fetchall()
         
         #update in balance table if entry exists
         if len(balanceRows) != 0:
            for br in balanceRows:
               oldQuantity = int(br["qty"])
            newQuantity = oldQuantity + qty
            
            cur.execute("UPDATE balance SET qty = ?  WHERE locationName = ? AND productName = ?",(newQuantity,to_location,productName) )
            con.commit()
      
      msg = "Movement successfully added"
      return msg

#add new movement
@app.route('/addMovement',methods = ['POST'])
def addMovement():
   try:
      if request.method == 'POST':
         atTime = request.form['atTime']
         from_location = request.form['from_location']
         to_location = request.form['to_location']
         productName = request.form['productName']
         qty = int(request.form['qty'])

         msg = movementManager(from_location,to_location,productName,qty)

         #only add movement if it has quantity left
         if msg == "Movement successfully added":
            with sql.connect("database.db") as con:
               con.row_factory = sql.Row
               cur = con.cursor()
               #entry for product movement table 
               cur.execute("INSERT INTO productmovement (atTime, from_location, to_location, productName, qty)VALUES (?,?,?,?,?)",(atTime,from_location,to_location,productName,qty))
               con.commit()
         
   except:
      con.rollback()
      msg = "error in insert operation"
   finally:
      return redirect(url_for('movementM')+"?msg="+msg)
      con.close()


#add new movement
@app.route('/editMovement',methods = ['POST'])
def editMovement():
   try:
      if request.method == 'POST':
         movementID = request.form['movementID']
         atTime = request.form['atTime']
         from_location = request.form['from_location']
         to_location = request.form['to_location']
         productName = request.form['productName']
         qty = int(request.form['qty'])
         editedqty = int(request.form['editedqty'])

         #update old entry from balance table
         old = movementManager(from_location,to_location,productName,-qty)

         if old == "Movement successfully added":
            msg = movementManager(from_location,to_location,productName,editedqty)

            #only update movement if it has quantity left
            if msg == "Movement successfully added":
               with sql.connect("database.db") as con:
                  con.row_factory = sql.Row
                  cur = con.cursor()
                  #entry for product movement table 
                  cur.execute("UPDATE productmovement SET  atTime = ? , from_location = ?, to_location = ? , productName = ? , qty = ? WHERE movementID = ?",(atTime, from_location, to_location, productName, editedqty, movementID) )
                  con.commit()
                  msg = "Movement Edited Successfully"
            else: 
               #revert if insuffecient quantity
               revert = movementManager(from_location,to_location,productName,qty)
               

   except:
      con.rollback()
      msg = "error in insert operation"
   finally:
      return redirect(url_for('movementM')+"?msg="+msg)
      con.close()

#delete movement
@app.route('/deleteMovement',methods = ['POST'])
def deleteMovement():
   try:
      if request.method == 'POST':
         movementID = request.form['movementID']
         from_location = request.form['from_location']
         to_location = request.form['to_location']
         productName = request.form['productName']
         qty = int(request.form['qty'])
         with sql.connect("database.db") as con:
            cur = con.cursor()

            if to_location !='-':
               #reduce quantity from to_location
               cur.execute("UPDATE balance SET qty = qty-?  WHERE locationName = ? AND productName = ?",(qty,to_location,productName) )
               con.commit()

            if from_location !='-':
               #add quantity to from_location
               cur.execute("UPDATE balance SET qty = qty+?  WHERE locationName = ? AND productName = ?",(qty,from_location,productName) )
               con.commit()

            cur.execute("DELETE FROM productmovement WHERE movementID = ?",(movementID,))
            con.commit()
            
            con.commit()
            msg = "Movement Deleted Successfully"
   except:
      con.rollback()
      msg = "error in delete operation"
   
   finally:
      return redirect(url_for('movementM')+"?msg="+msg)
      con.close()

#_______________________________Report Functions_______________________________________

#report management page
@app.route('/reportM')
def reportM():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from location")
   
   rows = cur.fetchall()
   
   #initalise empty lists for locations
   #listOfLists = [[] for i in range(totalLocations)]

   return render_template('reportM.html',rows = rows)

@app.route('/generatereport/<locName>')
def generatereport(locName):
   totalProducts = {}
   temp = 0

   con = sql.connect("database.db")
   con.row_factory = sql.Row

   cur = con.cursor()

   cur.execute("select * from products")
   productRows = cur.fetchall()

   for pr in productRows:
      cur.execute("select * from productmovement where to_location = ? AND productName = ? ",[locName,pr["productName"]])
      innerRowAdd = cur.fetchall()
      for ir in innerRowAdd:
         temp += int(ir["qty"])
      
      cur.execute("select * from productmovement where from_location = ? AND productName = ? ",[locName,pr["productName"]])
      innerRowSub = cur.fetchall()
      for ir in innerRowSub:
         temp -= int(ir["qty"])


      totalProducts[pr["productName"]] = temp
      temp = 0

   return render_template("generatereport.html",locName = locName, totalProducts = totalProducts)

if __name__ == '__main__':
   app.run(debug = True)
