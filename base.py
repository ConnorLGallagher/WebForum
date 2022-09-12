import os
from flask import Flask, render_template, session, redirect, url_for, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY']='oursecretkey'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class user(db.Model):
    __tablename__="users"

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.Text)
    password= db.Column(db.Text)
    userPosts= db.relationship('post',backref='user')
    userComments= db.relationship('comment',backref='user')
    userDiscussions= db.relationship('discussion',backref='user')

    def __init__(self, name, password):
        self.name=name
        self.password=password

class discussion(db.Model):
    __tablename__="discussions"

    id= db.Column(db.Integer, primary_key=True)
    postTitle= db.Column(db.Text)
    postContent= db.Column(db.Text)
    discPosts= db.relationship('post',backref='discussion')
    userThread= db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, postTitle, postContent, owner):
        self.postTitle=postTitle
        self.postContent=postContent
        self.userThread=owner

class post(db.Model):
    __tablename__="posts"

    id= db.Column(db.Integer, primary_key=True)
    postTitle= db.Column(db.Text)
    postContent= db.Column(db.Text)
    parentDiscussion= db.Column(db.Integer, db.ForeignKey('discussions.id'))
    postComments= db.relationship('comment',backref='post')
    userPost= db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, postTitle, postContent, parentDiscussion, owner):
        self.postTitle=postTitle
        self.postContent=postContent
        self.parentDiscussion=parentDiscussion
        self.userPost=owner

class comment(db.Model):
    __tablename__="comments"

    id= db.Column(db.Integer, primary_key=True)
    postContent= db.Column(db.Text)
    parentPost= db.Column(db.Integer, db.ForeignKey('posts.id'))
    userComment= db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, postContent, parentPost, owner):
        self.postContent=postContent
        self.parentPost=parentPost
        self.userComment=owner

def checkUpper(pword):
    result=False
    for i in pword:
        if i.isupper():
            result = True
            break
    return result
def checkLower(pword):
    result=False
    for i in pword:
        if i.islower():
            result = True
            break
    return result
def checkLength(pword):
    num=0
    for i in pword:
        num+=1
    if num>8:
        result=True
    else:
        result=False
    return result
def checkNum(pword):
    return (pword[-1].isdigit())

db.create_all()
@app.route('/', methods=['GET','POST'])
def index(): 
    discussions=discussion
    users=user  
    if request.method == "POST":
        title=request.form['title']
        content=request.form['content']
        us=request.cookies.get('User')
        if us is None:
            return redirect(url_for('signIn'))
        else:
            cuser=int(us)
            newpost=discussion(title,content,cuser)
            db.session.add(newpost)
            db.session.commit()
    return render_template('index.html',discussions=discussions,users=users)
@app.route('/profile', methods=['GET','POST'])
def profile(): 

    if request.method == "POST":
        user_name = request.form['name']
        pass_word = request.form['password']
        new_user = user(name=user_name, password=pass_word)
        test=user.query.filter_by(name=user_name).first()
        if test is not None:
            return redirect(url_for('signIn'))
        else:
            badlen= checkLength(pass_word)
            badup= checkUpper(pass_word)
            badlow= checkLower(pass_word)
            badnum= checkNum(pass_word)
            if(badlen and badup and badlow and badnum):
                db.session.add(new_user)
                db.session.commit()
            return render_template('report.html',badlen=badlen,badup=badup,badlow=badlow,badnum=badnum)
    else:
       return render_template("profile.html")
@app.route('/discussion/<localDiscussion>', methods=['GET','POST'])
def discussionPage(localDiscussion): 
    myDisc=discussion.query.get(localDiscussion)
    posts=myDisc.discPosts
    users=user
    url=url_for('discussionPage',localDiscussion=localDiscussion)
    if request.method == "POST":
        title=request.form['title']
        content=request.form['content']
        us=request.cookies.get('User')
        if us is None:
            return redirect(url_for('signIn'))
        cuser=int(us)
        newpost=post(title,content,localDiscussion,cuser)
        db.session.add(newpost)
        db.session.commit()
        myDisc=discussion.query.get(localDiscussion)
        posts=myDisc.discPosts
    return render_template('discussion.html',localDiscussion=localDiscussion,discussions=posts, users=users,url=url, curdisc=myDisc)
@app.route('/discussion/<localDiscussion>/<localPost>', methods=['GET','POST'])
def postPage(localDiscussion,localPost): 
    localDiscussion=localDiscussion
    mypost=post.query.get(localPost)
    users=user
    url=url_for('postPage',localDiscussion=localDiscussion,localPost=localPost)
    if request.method == "POST":
        content=request.form['comment']
        us=request.cookies.get('User')
        if us is None:
            return redirect(url_for('signIn'))
        cuser=int(us)
        newcomment=comment(content, localPost,cuser)
        db.session.add(newcomment)
        db.session.commit() 
    return render_template('post.html',item=mypost, users=users,url=url)
@app.route('/signIn', methods=['GET','POST'])
def signIn(): 
    if request.method == "POST":
        user_name = request.form['name']
        pass_word = request.form['password']
        test=user.query.filter_by(name=user_name).first()
        if test is None:
            return redirect(url_for('signIn'))
        elif(pass_word!=test.password):
            return redirect(url_for('signIn'))
        else:
            resp=make_response(render_template("signinsucsess.html"))
            resp.set_cookie('User',str(test.id))
            return resp
    return render_template("signIn.html")
@app.route('/signOut', methods=['GET','POST'])
def signOut():
    if request.method == "POST":
        resp=make_response(render_template("signoutsuc.html"))
        resp.set_cookie('User','',expires=0)
        return resp
    return render_template("signOut.html")
@app.route('/deletePost/<pid>', methods=['GET','POST'])
def deletePost(pid):
    pid=pid
    refpost=post.query.get(pid)
    us=request.cookies.get('User')
    if us is None:
        return redirect(url_for('signIn'))
    user=int(request.cookies.get('User'))
    if ((refpost.userPost)!=user):
        return redirect(url_for('signIn'))
    if request.method == "POST":
        delm=post.query.get(pid)
        db.session.delete(delm)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("deletePost.html",pid=pid)
@app.route('/deleteThread/<pid>', methods=['GET','POST'])
def deletediscussion(pid):
    pid=pid
    refpost=discussion.query.get(pid)
    us=request.cookies.get('User')
    if us is None:
        return redirect(url_for('signIn'))
    user=int(request.cookies.get('User'))
    if ((refpost.userThread)!=user):
        return redirect(url_for('signIn'))
    if request.method == "POST":
        delm=discussion.query.get(pid)
        db.session.delete(delm)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("deleteDiscussion.html",pid=pid)
@app.route('/deleteComment/<pid>', methods=['GET','POST'])
def deletecomment(pid):
    pid=pid
    refpost=comment.query.get(pid)
    us=request.cookies.get('User')
    if us is None:
        return redirect(url_for('signIn'))
    user=int(request.cookies.get('User'))
    if ((refpost.userComment)!=user):
        return redirect(url_for('signIn'))
    if request.method == "POST":
        delm=comment.query.get(pid)
        db.session.delete(delm)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template("deleteComment.html",pid=pid)
if __name__ == '__main__':
    app.run(debug=True)
