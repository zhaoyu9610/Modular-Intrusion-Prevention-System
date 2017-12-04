from flask import Flask, request, render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
#from flask_wtf import FlaskForm No need for form
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import accessdb 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=20)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_uesr(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username = request.form['usrn']).first()
        if user is not None:
            if check_password_hash(user.password, request.form['pswd']):
                login_user(user, remember=True)
                return redirect(url_for("index"))
        return abort(401)
    return render_template("login.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['usrn']).first()
        if user is None:
            newpswd = generate_password_hash(request.form['pswd'], method='sha256')
            print(newpswd)
            usr = User(username=request.form['usrn'], password = newpswd)
            db.session.add(usr)
            db.session.commit()
            login_user(usr, remember=True)
            return redirect(url_for("index"))
        return '<h1>The username has been already taken.</h1>', {'Content-Type': 'text/html'}
    return render_template("signup.html")

@app.route('/index')
@login_required
def index():
    #return '<h1>The uesr is successfully signed in.</h1>', {'Content-Type': 'text/html'}
    return render_template('index.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return '<h1>You\'ve logged out.</h1>', {'Content-Type': 'text/html'}

@app.route('/admin', methods = ['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form['usrn']
        password = request.form['pswd']
        if username == 'admin' and password == 'admin':
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(username = username, password = password)
                db.session.add(admin)
                db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for("adminControl"))
            return abort(401)
    return render_template("admin.html")

@app.route('/adminControl', methods=['POST', 'GET'])
@login_required
def adminControl():
    if request.method == "POST":
       	ips = []
        for key in request.form.keys():
            if(len(key) > 3 and key[:3] == 'ips'):
                ips.append(request.form[key])
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!s")
        if 'x' in request.form.keys():
            accessdb.updatexyz(request.form['x'], request.form['y'], request.form['z'])	
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!y")
	
        accessdb.add(ips)
        removingIps = []
        print(request.form)
        for key in request.form.keys():
            if(len(key)>=10 and key[:10] == 'removedips'):
                removingIps.append(request.form[key])
        print(removingIps)
        accessdb.remove(removingIps)
    #return '<h1>Invalid account or password</h1>', {'Content-Type': 'text/html'}
    x, y, z = accessdb.getxyz()
    return render_template("adminControl.html", content={'blacklists':accessdb.getBlackList(), 'x' : x, 'y':y, 'z': z})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)