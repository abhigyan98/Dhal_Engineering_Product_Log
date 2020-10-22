import sqlite3
import pandas.io.sql as sql
# import pdfkit


con = sqlite3.connect("list.db", check_same_thread=False)
db = con.cursor()
print("Database opened successfully")


############################# CATEGORY DB LOGIC ############################

def insertCategory(cid, name):
    db.execute("INSERT INTO category VALUES (?,?)", (cid, name))
    con.commit()


def fetchCategory():
    db.execute("SELECT * FROM category")
    categoryData = db.fetchall()
    return categoryData


def fetchSingleCategory(cid):
    db.execute("SELECT * FROM category WHERE cid=(?)", (cid,))
    sData = db.fetchall()
    return sData


def updateCategory(cid, name):
    db.execute("UPDATE category SET name=(?) WHERE cid=(?)",
               (name, cid))
    con.commit()


def deleteCategory(cid):
    db.execute("DELETE FROM category WHERE cid=(?)", (cid,))
    con.commit()

############################# SELLER DB LOGIC ############################

def insertSeller(sid, company, email, contact, phone):
    db.execute("INSERT INTO seller VALUES (?,?,?,?,?)",
               (sid, company, email, contact, phone))
    con.commit()


def fetchSeller():
    db.execute("SELECT * FROM seller")
    sellerData = db.fetchall()
    return sellerData


def fetchSingleSeller(sid):
    db.execute("SELECT * FROM seller WHERE sid=(?)", (sid,))
    sData = db.fetchall()
    return sData


def updateSeller(sid, company, email, contact, phone):
    db.execute("UPDATE seller SET company=(?),email=(?),contact=(?),phone=(?) WHERE sid=(?)",
               (company, email, contact, phone, sid))
    con.commit()


def deleteSeller(sid):
    db.execute("DELETE FROM seller WHERE sid=(?)", (sid,))
    con.commit()

############################ CLIENT DB LOGIC ############################


def insertClient(clid, name, orderno, gstno, clientAddress, siteAddress, contact, mobile, email):
    db.execute("INSERT INTO client VALUES (?,?,?,?,?,?,?,?,?)",
               (clid, name, orderno, gstno, clientAddress, siteAddress, contact, mobile, email))
    con.commit()


def fetchClient():
    db.execute("SELECT * FROM client")
    clientData = db.fetchall()
    return clientData


def fetchSingleClient(clid):
    db.execute("SELECT * FROM client WHERE clid=(?)", (clid,))
    cData = db.fetchall()
    return cData


def updateClient(clid, name, orderno, gstno, clientAddress, siteAddress, contact, mobile, email):
    db.execute("UPDATE client SET name=(?),orderno=(?),gstno=(?),clientAddress=(?),siteAddress=(?),contact=(?),mobile=(?),email=(?) WHERE clid=(?)",
               (name, orderno, gstno, clientAddress, siteAddress, contact, mobile, email, clid))
    con.commit()


def deleteClient(clid):
    db.execute("DELETE FROM client WHERE clid=(?)", (clid,))
    con.commit()


############################ ITEM DB LOGIC ############################


def insertItem(iid, category, name, seller, hsn, quantity, unit, rate, date):
    db.execute("INSERT INTO item VALUES (?,?,?,?,?,?,?,?,?)",
               (iid, category, name, seller, hsn, quantity, unit, rate, date))
    con.commit()


def fetchItem():
    db.execute("SELECT * FROM item")
    itemData = db.fetchall()
    return itemData


def fetchSingleItem(iid):
    db.execute("SELECT * FROM item WHERE iid=(?)", (iid,))
    sitemData = db.fetchall()
    return sitemData


def updateItem(iid, category, name, seller, hsn, quantity, unit, rate, date):
    db.execute("UPDATE item SET category=(?),name=(?),seller=(?),hsn=(?),quantity=(?),unit=(?),rate=(?),date=(?) WHERE iid=(?)",
               (category, name, seller, hsn, quantity, unit, rate, date, iid))
    con.commit()


def deleteItem(iid):
    db.execute("DELETE FROM item WHERE iid=(?)", (iid,))
    con.commit()


############################# EXCEL DB LOGIC ############################

def toCategoryExcel():
    db.execute("SELECT * FROM category")
    itemData = db.fetchall()
    csvList = []
    csvList.append(['cid', 'name'])
    for data in itemData:
        csvList.append(data)
    return csvList

def toSellerExcel():
    db.execute("SELECT * FROM seller")
    itemData = db.fetchall()
    csvList = []
    csvList.append(['sid', 'company', 'email', 'contact', 'phone'])
    for data in itemData:
        csvList.append(data)
    return csvList

def toClientExcel():
    db.execute("SELECT * FROM client")
    itemData = db.fetchall()
    csvList = []
    csvList.append(['clid', 'name', 'orderno', 'gstno', 'clientAddress', 'siteAddress', 'contact', 'mobile', 'email'])
    for data in itemData:
        csvList.append(data)
    return csvList

def toItemExcel():
    db.execute("SELECT * FROM item")
    itemData = db.fetchall()
    csvList = []
    csvList.append(['iid', 'category', 'name', 'seller',
                    'hsn', 'quantity', 'unit', 'rate', 'date'])
    for data in itemData:
        csvList.append(data)
    return csvList
