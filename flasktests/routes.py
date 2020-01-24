from flask import Flask, render_template, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
from flasktests import app, bcrypt
from flasktests.forms import RegistrationForm, LoginForm, PostForm
from flasktests.models import User, Post


@app.route("/")
@app.route("/home")
def home():
    posts_db = Post.find()
    # print("posts_db  "  , posts_db)
    posts = []
    for post in posts_db:
        # print("post.author " , post['author'])
        post_user = User.get_by_id(post['author'])
        post['username'] = post_user.username
        posts.append(post)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    # print("current_user " , current_user)
    if current_user and current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = form.username.data.strip()
        email = form.email.data.strip()

        find_user = User.get_by_email(email)
        if find_user is None:
            User.register(username, email, hashed_password)
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Account already exists for {username}!', 'success')

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = User.get_by_email(email)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("user", user)
            from flask import current_app
            print("userid: ", getattr(user, current_app.login_manager.id_attribute)())
            print("user type ", type(user))

            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/acoount")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_post = Post(title, content, current_user.get_id())
        # print(title, content, current_user.get_id())
        new_post.save()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<string:post_id>")
def post(post_id):
    post = Post.get_by_id(post_id)
    # print("posts  ", post)
    post_user = User.get_by_id(post['author'])
    # print(post_user.username)
    post['username'] = post_user.username
    # print(current_user._id)
    # print(post['author'])
    return render_template('post.html', post=post)


@app.route("/user/<string:username>")
def user_posts(username):

    user_name = User.get_by_id(username)
    user = user_name.username
    posts_db = Post.find({"author": username})
    post_count = posts_db.count()
    posts = []
    for post in posts_db:
        # print("post.author " , post['author'])
        post_user = User.get_by_id(post['author'])
        post['username'] = post_user.username
        posts.append(post)
    return render_template('user_posts.html', user=user, posts=posts, post_count=post_count)