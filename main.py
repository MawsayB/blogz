from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True   
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:mbadded@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'xQlpp426ff'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title 
        self.content = content 
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship(Blog, backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog' , 'display_signup_form', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', page_heading = "Write a Bloggity Blog Post!")

@app.route('/blog', methods=['POST', 'GET'])
def blog(): 
    id = request.args.get('id')
    user = request.args.get('user')
    all_users = User.query.all()

    if id == None:
        post = Blog.query.all()
        user = User.query.all()
        return render_template('all_entries.html', page_heading = "The Incredible Bloggity Blog!", 
        post=post, user=user)  

    if id:
        post = Blog.query.get(id)
        user = Blog.query.filter_by(owner_id=id).all()
        return render_template('one_entry.html', page_heading = "I Built a Bloggity Blog!", post=post, user=user)

    if user:
        user = User.query.get(id)
        post = Blog.query.filter_by(owner_id=id).all()        
        return render_template('singleUser.html', page_heading = "Writer Spotlight", post=post, user=user)
        
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    blog_id = None 

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        owner = User.query.filter_by(username=session['username']).first()

        title_error=''
        content_error=''

        if len(title) == 0:
            title_error = "Don't forget to add a title to your entry!"
        if len(content) == 0:
            content_error = "Don't you want to write something?"  

        if title_error or content_error:
            return render_template('add_entry.html', page_heading="Add a Blog Entry", title=title, 
            title_error=title_error, content=content, content_error=content_error)
        else:
            new_post = Blog(title, content, owner)
            db.session.add(new_post)
            db.session.commit()
            blogs = Blog.query.all()

            user_id = str(new_post.owner_id)
            return redirect('/blog?id=' + user_id)
    
    return render_template('add_entry.html', page_heading = "Add a Blog Entry", title='', title_error='',
    content='', content_error='', user_id=user_id)

@app.route('/', methods=['POST', 'GET'])
def index(): 
    id = request.args.get('id')
    user = User.query.all()
    return render_template('index.html', page_heading = "The Incredible Bloggity Blog!", user=user)   

@app.route('/signup')
def display_signup_form():
    return render_template('signup.html', page_heading = "Become a Bloggity Blog Writer", 
    username='', username_error='', password='', password_error='', verpassword='', verpassword_error='')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verpassword = request.form['verpassword']

        username_error=''
        password_error=''
        verpassword_error=''

        if len(username) == 0:
            username_error = 'Please enter a username.'
        if len(username) >= 1 and len(username) < 3:
            username_error = 'Please re-enter a username that is at least 3 characters long.'

        if len(password) == 0:
            password_error = 'Please enter a password.'
        if len(password) >= 1 and len(password) < 3:
            password_error = 'Please re-enter a password that is at least 3 characters long.'

        if len(verpassword) == 0:
            verpassword_error = 'Please verify your password.'
        if verpassword != verpassword.replace(verpassword, password):
            verpassword_error = 'Passwords do not match. Try again.'

        if not username_error and not password_error and not verpassword_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('Write your first post below...')
                return redirect('/newpost')
            else:
                return "<h3>That username already exists.</h3>"

    return render_template('signup.html', page_heading = "Become a Bloggity Blog Writer",
        username=username, username_error=username_error, password='', password_error=password_error, 
        verpassword='', verpassword_error=verpassword_error)

if __name__ == '__main__':
    app.run() 