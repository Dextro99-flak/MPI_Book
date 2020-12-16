from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
import sqlalchemy.orm
import urllib.request, urllib.parse, urllib.error
import json
def info11(isbn):
    descp=""
    fh = urllib.request.urlopen('https://www.googleapis.com/books/v1/volumes?q=isbn+'+isbn)
    js1=""
    for line in fh :
        js1=js1+ line.decode()
    info = json.loads(js1)
    s1 = info.get("items")
    s2 = s1[0]
    return s2.get("volumeInfo").get("description")
def info12(isbn):
    fh = urllib.request.urlopen('https://www.googleapis.com/books/v1/volumes?q=isbn+' + isbn)
    js1 = ""
    for line in fh:
        js1 = js1 + line.decode()
    info = json.loads(js1)
    s1 = info.get("items")
    s2 = s1[0]
    return s2.get("volumeInfo").get("imageLinks").get("thumbnail")



app = Flask(__name__)
#index.html is the main login screen
#error.html will contain a message to go back to login screen as the details were wrong
#register.html will give data to register_app() to get user registered
#no_login.html will display login error
#search.html will give search data to search_app()
#search_results.html shows the search results
#search_reviews.html is very similar to search_results.html only it won't be taking any input
#bookpage.html shows the book information and the books reviews



# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://flwbrezdhdlxrb:22593920f1bf783c0923df8a463b5ac80d0fae37e5d3179bc2b7850f8bc642ee@ec2-52-72-65-76.compute-1.amazonaws.com:5432/d7r8k65uhc7fub")
db = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html",messsage=" ")


@app.route('/search',methods=["POST","GET"])
def login_app():
    username=request.form.get("uname")
    password=request.form.get("pass")
    nme = db.execute("SELECT * FROM users WHERE (username = :uname)AND(password =  :pass)",{"uname":username,"pass":password})
    db.commit()
    if db.execute("SELECT * FROM users WHERE (username = :uname)AND(password =  :pass)",{"uname":username,"pass":password}).rowcount == 0 :
        #return render_template("error.html")
        return render_template("index.html",mes="Invalid Password or Username")
    else :
        session["username"]=username
        session["login"]='successful'
        return render_template("search.html",var=session.get("login"))

@app.route('/search/search_result',methods=["POST","GET"])
def search_app():
    text=request.form.get("query")
    text2 = '%'+text+'%'
    info1 = db.execute("SELECT author FROM books WHERE (isbn= :text)OR(title= :text)OR(author= :text)",{"text":text})
    info2 = db.execute("SELECT * FROM books WHERE (isbn LIKE :text )OR(title LIKE :text)OR(author LIKE :text)",{"text":text2} )
    db.commit()
    ret=info2.fetchall()
    #return '<h1>'+str(ret)+'</ret>'
    return render_template("search_results.html", var=session.get("login"), info1=ret)


@app.route('/search/search_result/<string:isbn>',methods=["POST","GET"])
def result_app(isbn):
    if session["login"] != 'successful' :
        render_template('index.html', mes=' ')
    review=request.form.get('revtext')
    info = 11  #Use Goodreads API to input book info
    db.execute("INSERT INTO reviews ( isbn, username, text_review ) VALUES (:isbn , :uname , :rev)",{"isbn":isbn,"uname":session.get('username'),"rev":review})
    db.commit()
    return render_template("search_reviews.html", var=session.get("login"), isbn=isbn , lnk=info12(isbn) ,desc=info11(isbn) ,uname=session.get('username'), rev=review) #add info to the arguments


@app.route('/register',methods=['GET','POST'])
def register_app():
    username=request.form.get('uname')
    password1=request.form.get('pass1')
    password2=request.form.get('pass2')
    ss = db.execute("SELECT * FORM users WHERE (username = :uname)",{"uname":username})
    if password1==password2 :
        if ss.rowcount == 0 :
            db.execute("INSERT INTO users (username , password) VALUES ( :uname , :pass )",{"uname":username,"pass":password1})
            db.commit()
            return render_template("register.html",message="Registration Sucessful")
        else:
            return render_template("register.html",message="Username not available, use a more unique one")
    else:
        return render_template("register.html",message="Registration Unsucessful")



@app.route('/logout',methods=["POST"])
def logout_app():
    session["login"]="not_in"
    m  = session["login"]+"Logged out successfully"
    return render_template("index.html",mes=m)

