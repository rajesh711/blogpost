import os
import secrets

from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask.globals import current_app
from flask_login import login_user, current_user, logout_user, login_required
from flasktests import app, bcrypt
from flasktests.forms import RegistrationForm, LoginForm, PostForm, UpdateAccountForm
from flasktests.models import User, Post
from PIL import Image


@app.route("/")
@app.route("/home")
def home():
    posts_db = Post.find()
    posts = []
    for post in posts_db:
        post_user = User.get_by_id(post['author'])
        post['username'] = post_user.username
        post['image'] = post_user.image

        posts.append(post)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
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

            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        user_id = current_user.get_id()
        print(user_id)
        result = User.get_by_id(user_id)
        new_val = {"username": current_user.username, "email": current_user.email, "image": current_user.image}

        User.update_by_user_id(user_id, new_val)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


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
        new_post.save()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@app.route("/post/<string:post_id>")
def post(post_id):
    post = Post.get_by_id(post_id)
    post_user = User.get_by_id(post['author'])
    post['username'] = post_user.username
    post['image'] = post_user.image
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
        post['image'] = post_user.image
        posts.append(post)
    return render_template('user_posts.html', user=user, posts=posts, post_count=post_count)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/admin")
def admin():
    user_data = User.get_all()
    users = []
    for user in user_data:
        post = Post.find({"author": str(user['_id'])})
        total_post = post.count()
        user['total'] = total_post
        users.append(user)
    return render_template('admin_panel.html', title='admin', users=users)


@app.route("/post/<string:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    delete_result = Post.delete_by_id(post_id)
    if delete_result:
        flash('Your post has been deleted!', 'success')
    else:
        flash('Your post not deleted!', 'info')
    return redirect(url_for('home'))


@app.route("/post/<string:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.get_by_id(post_id)
    print(type(post))
    if post['author'] != current_user.get_id():
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post['title'] = form.title.data
        post['content'] = form.content.data
        Post.update_by_id(post_id, post)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

