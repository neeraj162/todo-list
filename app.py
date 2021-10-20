from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy.orm import session
from werkzeug.utils import redirect
app = Flask(__name__)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,login_user, logout_user, login_required, current_user, LoginManager

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app) 

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    notes = db.relationship('Todo')


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # def __repr__(self) -> str:
    #     return f"{self.id} - {self.title}"




@app.route("/", methods=['GET','POST'])
@login_required
def hello_world():
    if(request.method=="POST"):
        title = request.form.get("title")
        desc = request.form.get("desc")
        todo  = Todo(title=title,desc=desc,user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
    return render_template('index.html', user=current_user)
    # return "<p>Hello, World!</p>"

@app.route("/about")
@login_required
def about():
    return render_template('about.html')

@app.route("/update/<int:id>", methods=['GET','POST'])
@login_required
def update(id):
    if request.method=='POST':
        title = request.form.get("title")
        desc = request.form.get("desc")
        todo = Todo.query.filter_by(id=id).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()  
        return redirect('/') 
    todo = Todo.query.filter_by(id=id).first()
    return render_template('update.html', todo=todo)

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("floatingInput")
        password = request.form.get("floatingPassword")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Succesfully', category='success')
                login_user(user, remember=True)
                return redirect('/')
            else:
                flash('Incorrect Email/Password , try again...', category='error')
        else:
            flash('Email does not exist...', category='error')

    return render_template("login.html")

@app.route("/sign-up", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("floatingInput")
        first_name = request.form.get("firstName")
        password1 = request.form.get("floatingPassword")
        password2 = request.form.get("floatingPassword1")
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists..',category='error')
        elif len(email) < 5:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name)<2:
            flash('Your name must atleast have 2 characters', category='error')
        elif password1 !=password2:
            flash('Passwords does not match', category='error')
        elif len(password1)<7:
            flash('Password must atleast contain 7 characters', category='error')
        else:
            # good to go and add it to database
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            print(new_user)
            login_user(new_user, remember=True)
            flash("Account created Successfully..", category='success')
            return redirect('/')
               
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    app.secret_key = 'todo-list'
    app.run(debug=True, port=8000)