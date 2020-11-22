from flask import *
import os
import uuid
import listdb
import logindb
import io
import csv
import datetime as dt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

app = Flask(__name__, static_url_path='')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.secret_key = 'secret-f22c8e2e-d0e9-490f-9be8-17769ccc1316'
link = 'http://127.0.0.1:3000'

# # Set environment variables testing
os.environ['ADMIN_EMAIL'] = '<ADMIN_EMAIL>'
os.environ['ADMIN_EMAIL_PASSWORD'] = '<ADMIN_PASS>'
os.environ['VERIFYING_EMAIL'] = '<VERIFYING_EMAIL>'


# Get environment variables
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')
VERIFYING_EMAIL = os.getenv('VERIFYING_EMAIL')


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):

    # defining function
    return render_template("404.html")


################# LOGIN FRONTEND LOGIC ########################


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signin", methods=["POST"])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")
    userData = logindb.getPasswordForLogin(email)

    try:
        if(password == userData[0][1] and userData[0][2] == "ACTIVATED"):
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('uid', userData[0][0], max_age=60*60*24*365)
            return resp
        else:
            flash("User Account Not Activated", "warning")
            return redirect(url_for('login'))
    except IndexError as e:
        flash("User Account Does Not Exist", "danger")
        return redirect(url_for('login'))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name").upper()
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    allEmail = logindb.getAllUserEmail()
    for e in allEmail:
        if email == e[0]:
            msg = "User already has an account"
            flash(msg, "warning")
            return redirect(url_for('login'))

    uid = str(uuid.uuid4())
    active = "NOT ACTIVE"
    if(password1 == password2):
        logindb.createUser(uid, name, email,  password1, active)

    flash("User Registered Successfully. Access will be granted after admin verification", "secondary")

    # SUBJECT = "Dhal Engineering IT Portal - User Account Activation Request"
    # TEXT = f"""
    # An User has registered with our services.\n
    # His/Her details are :\n
    # NAME: {name},
    # EMAIL: {email}\n\n
    # To verify his/her identity, click the link below\n
    # {link}/user/{uid}/verify_identity
    # """

    # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    # server = smtplib.SMTP("smtp.gmail.com", 587)
    # server.ehlo()
    # server.starttls()
    # server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    # # this email is supposed to go to arijit from dhal
    # server.sendmail(ADMIN_EMAIL, VERIFYING_EMAIL, message)
    # server.close()

    
    msg = MIMEMultipart('alternative')
    msg['Subject']='Dhal Engineering IT Portal - User Account Activation Request'
    msg['From'] = formataddr((str(Header('Dhal Engineering', 'utf-8')), ADMIN_EMAIL))
    msg['To'] = VERIFYING_EMAIL

    html =  f"""
        An User has registered with our services.<br><br>\n
        His/Her details are :<br><br>\n
        NAME: {name},<br>
        EMAIL: {email}\n\n
        <br><br>
        To verify his/her identity, click the link :<br><br> \n
        {link}/user/{uid}/verify_identity
        """

    # Record the MIME types of text/html.
    msg.attach(MIMEText(html, 'html'))

    # Send the message via local SMTP server.
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(ADMIN_EMAIL, VERIFYING_EMAIL, msg.as_string())
    s.quit()


    return redirect(url_for('login'))


@app.route("/user/<uid>/verify_identity")
def redirectToVerification(uid):
    data = logindb.getUser(uid)
    userEmail = data[0][2]
    print(userEmail)
    active = "ACTIVATED"
    resp = logindb.updateUserActivation(uid, active)

    response = "User Verified Successfully"

    # SUBJECT = "Dhal Engineering IT Portal - User Account Activated"
    # TEXT = f"""
    # Admin has verified your identity.\n
    # You can now login using your provided 'EMAIL' and 'PASSWORD' in\n
    # {link}/login
    # """

    # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

    # server = smtplib.SMTP("smtp.gmail.com", 587)
    # server.ehlo()
    # server.starttls()
    # server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    # server.sendmail(ADMIN_EMAIL, userEmail, message)
    # server.close()
    
    msg = MIMEMultipart('alternative')
    msg['Subject']='Dhal Engineering IT Portal - User Account Activated'
    msg['From'] = formataddr((str(Header('Dhal Engineering', 'utf-8')), ADMIN_EMAIL))
    msg['To'] = userEmail

    html =  f"""
        Admin has verified your identity.<br>\n
        You can now login using your provided 'EMAIL' and 'PASSWORD' at<br><br>\n
        {link}/login
        """

    # Record the MIME types of text/html.
    msg.attach(MIMEText(html, 'html'))

    # Send the message via local SMTP server.
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(ADMIN_EMAIL, userEmail, msg.as_string())
    s.quit()

    return jsonify(response)


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('uid', expires=0)
    return resp

################# INDEX FRONTEND LOGIC ########################


@app.route("/")
def index():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        email = data[0][2]
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        time = curDate.strftime("%H:%M")
        timestamp = day + ", at " + time
        return render_template("index.html", name=name, email=email, timestamp=timestamp)
    else:
        return redirect(url_for('login'))

################# CATEGORY FRONTEND LOGIC ########################


@app.route("/category")
def category():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        categoryData = listdb.fetchCategory()
        return render_template("category.html", categoryData=categoryData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/addCategory", methods=["POST"])
def addCategory():
    if (request.cookies.get('uid')):
        if request.method == "POST":
            cid = str(uuid.uuid4())
            name = str(request.form.get("name")).upper()
            listdb.insertCategory(cid, name)
            flash("Category Added Successfully", "primary")
            return redirect(url_for('category'))
    else:
        return redirect(url_for('login'))


@app.route("/categoryUpdate/<cid>", methods=["GET"])
def categoryUpdate(cid):
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        singleCategory = listdb.fetchSingleCategory(cid)
        sData = []
        for i in singleCategory:
            sData.append(i)
        return render_template("categoryUpdate.html", sData=sData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/updatedCategory/<cid>", methods=["POST"])
def updatedCategory(cid):
    if (request.cookies.get('uid')):
        if request.method == "POST":
            name = str(request.form.get("name")).upper()
            listdb.updateCategory(cid, name)
            flash("Category Updated Successfully", "success")
            return redirect(url_for('category'))
    else:
        return redirect(url_for('login'))


@app.route("/categoryDelete/<cid>", methods=["GET", "POST"])
def categoryDelete(cid):
    if (request.cookies.get('uid')):
        listdb.deleteCategory(cid)
        flash("Category Deleted Successfully", "danger")
        return redirect(url_for('category'))
    else:
        return redirect(url_for('login'))


################# SELLER FRONTEND LOGIC ########################


@app.route("/seller")
def seller():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        sellerData = listdb.fetchSeller()
        return render_template("seller.html", sellerData=sellerData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/addSeller", methods=["POST"])
def addSeller():
    if (request.cookies.get('uid')):
        if request.method == "POST":
            sid = str(uuid.uuid4())
            company = str(request.form.get("company")).upper()
            email = str(request.form.get("email"))
            contact = str(request.form.get("contact")).upper()
            phone = (request.form.get("phone"))
            listdb.insertSeller(sid, company, email, contact, phone)
            flash("Seller Added Successfully", "primary")
            return redirect(url_for('seller'))
    else:
        return redirect(url_for('login'))


@app.route("/sellerUpdate/<sid>", methods=["GET"])
def sellerUpdate(sid):
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        singleSeller = listdb.fetchSingleSeller(sid)
        sData = []
        for i in singleSeller:
            sData.append(i)
        return render_template("sellerUpdate.html", sData=sData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/updatedSeller/<sid>", methods=["POST"])
def updatedSeller(sid):
    if (request.cookies.get('uid')):
        if request.method == "POST":
            company = str(request.form.get("company")).upper()
            email = str(request.form.get("email"))
            contact = str(request.form.get("contact")).upper()
            phone = (request.form.get("phone"))
            listdb.updateSeller(sid, company, email, contact, phone)
            flash("Seller Updated Successfully", "success")
            return redirect(url_for('seller'))
    else:
        return redirect(url_for('login'))


@app.route("/sellerDelete/<sid>", methods=["GET", "POST"])
def sellerDelete(sid):
    if (request.cookies.get('uid')):
        listdb.deleteSeller(sid)
        msg = "record successfully deleted!"
        flash("Seller Deleted Successfully", "danger")
        return redirect(url_for('seller'))
    else:
        return redirect(url_for('login'))
################# CLIENT FRONTEND LOGIC ########################


@app.route("/client")
def client():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        cdata = listdb.fetchClient()
        clientData = []
        for i in cdata:
            clientData.append(i)
        # print(clientData)
        return render_template('client.html', clientData=clientData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/addClient", methods=["POST"])
def addClient():
    if (request.cookies.get('uid')):
        if request.method == "POST":
            clid = str(uuid.uuid4())
            name = str(request.form.get("name")).upper()
            orderno = str(request.form.get("orderno"))
            gstno = str(request.form.get("gstno"))
            clientAddress = (request.form.get("clientAddress")).upper()
            siteAddress = (request.form.get("siteAddress")).upper()
            contact = str(request.form.get("contact")).upper()
            email = str(request.form.get("email"))
            mobile = str(request.form.get("mobile"))
            listdb.insertClient(clid, name, orderno, gstno,
                                clientAddress, siteAddress, contact, mobile, email)
            flash("Client Added Successfully", "primary")
            return redirect(url_for('client'))
    else:
        return redirect(url_for('login'))


@app.route("/clientUpdate/<clid>", methods=["GET"])
def clientUpdate(clid):
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        singleClient = listdb.fetchSingleClient(clid)
        clData = []
        for i in singleClient:
            clData.append(i)
        return render_template("clientUpdate.html", clData=clData, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/updatedClient/<clid>", methods=["POST"])
def updatedClient(clid):
    if (request.cookies.get('uid')):
        if request.method == "POST":
            name = str(request.form.get("name")).upper()
            orderno = str(request.form.get("orderno"))
            gstno = str(request.form.get("gstno"))
            clientAddress = (request.form.get("clientAddress")).upper()
            siteAddress = (request.form.get("siteAddress")).upper()
            contact = str(request.form.get("contact")).upper()
            email = str(request.form.get("email"))
            mobile = str(request.form.get("mobile"))
            listdb.updateClient(clid, name, orderno, gstno,
                                clientAddress, siteAddress, contact, mobile, email)
            flash("Client Updated Successfully", "success")
            return redirect(url_for('client'))
    else:
        return redirect(url_for('login'))


@app.route("/clientDelete/<clid>", methods=["GET", "POST"])
def clientDelete(clid):
    if (request.cookies.get('uid')):
        listdb.deleteClient(clid)
        msg = "record successfully deleted!"
        flash("Client Deleted Successfully", "danger")
        return redirect(url_for('client'))
    else:
        return redirect(url_for('login'))
################ ITEM FRONTEND LOGIC ########################


@app.route("/item")
def item():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        # to feed the array of category,seller
        cData = listdb.fetchCategory()
        sData = listdb.fetchSeller()
        clist = []
        slist = []
        for i in cData:
            clist.append(i[1])
        for j in sData:
            slist.append(j[1])
        return render_template("item.html", clist=clist, slist=slist, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/addItem", methods=["POST"])
def addItem():
    if (request.cookies.get('uid')):
        if request.method == "POST":
            iid = str(uuid.uuid4())
            category = str(request.form.get("category")).upper()
            name = str(request.form.get("name")).upper()
            seller = str(request.form.get("seller")).upper()
            hsn = (request.form.get("hsn"))
            quantity = (request.form.get("quantity"))
            unit = (request.form.get("unit"))
            rate = (request.form.get("rate"))
            date = (request.form.get("date"))
            listdb.insertItem(iid, category, name, seller,
                              hsn, quantity, unit, rate, date)
            flash("Item Added Successfully", "primary")
            return redirect(url_for('list'))
    else:
        return redirect(url_for('login'))


@app.route("/itemUpdate/<iid>", methods=["GET"])
def itemUpdate(iid):
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        singleItem = listdb.fetchSingleItem(iid)
        sItem = []
        cData = listdb.fetchCategory()
        sData = listdb.fetchSeller()
        clist = []
        slist = []
        for i in cData:
            clist.append(i[1])
        for j in sData:
            slist.append(j[1])
        for i in singleItem:
            sItem.append(i)
        return render_template("itemUpdate.html", sItem=sItem, clist=clist, slist=slist, name=name)
    else:
        return redirect(url_for('login'))


@app.route("/updatedItem/<iid>", methods=["POST"])
def updatedItem(iid):
    if (request.cookies.get('uid')):
        if request.method == "POST":
            category = str(request.form.get("category")).upper()
            name = str(request.form.get("name")).upper()
            seller = str(request.form.get("seller")).upper()
            hsn = (request.form.get("hsn"))
            quantity = (request.form.get("quantity"))
            unit = (request.form.get("unit"))
            rate = (request.form.get("rate"))
            date = str(request.form.get("date"))
            listdb.updateItem(iid, category, name, seller,
                              hsn, quantity, unit, rate, date)
            flash("Item Updated Successfully", "success")
            return redirect(url_for('list'))
    else:
        return redirect(url_for('login'))


@app.route("/itemDelete/<iid>", methods=["GET", "POST"])
def itemDelete(iid):
    if (request.cookies.get('uid')):
        listdb.deleteItem(iid)
        msg = "Item Deleted Successfully"
        flash(msg, "danger")
        return redirect(url_for('list'))
    else:
        return redirect(url_for('login'))

################# LIST FRONTEND LOGIC ########################


@app.route("/list")
def list():
    if (request.cookies.get('uid')):
        uid = request.cookies.get('uid')
        data = logindb.getUser(uid)
        name = data[0][1]
        # fetch item
        itemData = listdb.fetchItem()
        return render_template("list.html", itemData=itemData, name=name)
    else:
        return redirect(url_for('login'))

################# EXCEL FRONTEND LOGIC ########################


@app.route('/categoryExcel')
def categoryExcel():
    if (request.cookies.get('uid')):
        csvList = listdb.toCategoryExcel()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csvList)
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        # time = curDate.strftime("%H:%M")
        # timestamp = day + ", at " + time
        filename = "CategoryStatement-"+day
        resp = make_response(si.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            filename)
        return resp
    else:
        return redirect(url_for('login'))


@app.route('/sellerExcel')
def sellerExcel():
    if (request.cookies.get('uid')):
        csvList = listdb.toSellerExcel()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csvList)
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        # time = curDate.strftime("%H:%M")
        # timestamp = day + ", at " + time
        filename = "SellerStatement-"+day
        resp = make_response(si.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            filename)
        return resp
    else:
        return redirect(url_for('login'))


@app.route('/clientExcel')
def clientExcel():
    if (request.cookies.get('uid')):
        csvList = listdb.toClientExcel()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csvList)
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        # time = curDate.strftime("%H:%M")
        # timestamp = day + ", at " + time
        filename = "ClientStatement-"+day
        resp = make_response(si.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            filename)
        return resp
    else:
        return redirect(url_for('login'))


@app.route('/itemExcel')
def itemExcel():
    if (request.cookies.get('uid')):
        csvList = listdb.toItemExcel()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csvList)
        curDate = dt.datetime.now()
        day = curDate.strftime("%d-%m-%Y")
        # time = curDate.strftime("%H:%M")
        # timestamp = day + ", at " + time
        filename = "ItemStatement-"+day
        resp = make_response(si.getvalue())
        resp.headers['Content-Type'] = 'text/csv'
        resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            filename)
        return resp
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
