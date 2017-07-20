from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import configparser,os 

app = Flask(__name__)
app.config['DEBUG'] = True

dbconfig = configparser.ConfigParser()
dbconfig.read("db-info.ini")
uristring = dbconfig.get("dbconfig","mysecret")
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('DATABASE_URL', uristring)
app.config['SQLALCHEMY_ECHO']=True
db = SQLAlchemy(app)

class Post(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    title=db.Column(db.String(120))
    body=db.Column(db.Text)
    date=db.Column(db.DateTime, nullable=False)
    draft=db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, title, body, draft):
        self.title=title
        self.body=body
        self.draft=draft
        self.date=datetime.now()

@app.route('/', methods=['GET'])
def index():
    posts = Post.query.all()
    return render_template("blog.html",posts=posts, title="JMN BAB Blog")

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title_error = ""
        body_error = ""
        post_title = request.form['title']
        if len(post_title) == 0 or post_title == "":
            title_error = "Title field may not be empty."
        post_body = request.form['body']
        if len(post_body) == 0 or post_body == "":
            body_error = "Post content field may not be empty."
        post_draft = request.form.get('draft')
        
        # handle errors and redirect
        if title_error or body_error:
            return render_template('new-post.html', 
                    post_title=post_title,
                    title_error=title_error,
                    post_body=post_body,
                    body_error=body_error)

        new_post=Post(post_title,post_body,post_draft)
        db.session.add(new_post)
        db.session.commit()
        post = Post.query.filter_by(id=new_post.id).all()
        return render_template('single-post.html', post=post)  
    return render_template("new-post.html")

@app.route('/single', methods=['POST','GET'])
def show_post():
    post_id=request.args['id']
    post=Post.query.filter_by(id=post_id).all()
    return render_template('single-post.html', post=post)

@app.route('/blog', methods=['GET'])
def get_posts():
    return redirect('/')

if __name__ == '__main__':
    app.run()
