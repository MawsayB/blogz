from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True   
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:mbmadethis@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(2500))

    def __init__(self, title, content):
        self.title = title 
        self.content = content 

@app.route('/blog', methods=['POST', 'GET'])
def index(): 
    id = request.args.get('id')

    if id == None:
        post = Blog.query.all()
        return render_template('base.html', page_heading = "I Built a Bloggity Blog!", post=post)   
    else:
        post = Blog.query.get(id)
        return render_template('one_entry.html', page_heading = "I Built a Bloggity Blog!", post=post)
        
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        title_error=''
        content_error=''

        if len(title) == 0:
            title_error = "Don't forget to add a title to your entry!"
        if len(content) == 0:
            content_error = "Don't you want to write something?"

        if title_error or content_error:
            return render_template('add_entry.html', page_heading="Add a Blog Entry", title=title, title_error=title_error, content=content, content_error=content_error)
        else:
            new_post = Blog(title, content)
            db.session.add(new_post)
            db.session.commit()

            id = str(new_post.id)
            return redirect('/blog?id=' + id)
    
    return render_template('add_entry.html', page_heading = "Add a Blog Entry", title='', title_error='', 
    content='', content_error='')

if __name__ == '__main__':
    app.run() 