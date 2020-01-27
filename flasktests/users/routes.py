from flask import Flask, render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flasktests import bcrypt

from flasktests.models import User, Post
from flasktests.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flasktests.users.utils import save_picture

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
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
            return redirect(url_for('users.login'))
        else:
            flash(f'Account already exists for {username}!', 'success')

    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user = User.get_by_email(email)

        if user and bcrypt.check_password_hash(user.password, form.password.data):

            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/user/<string:username>")
def user_posts(username):
    user_name = User.get_by_id(username)
    user = user_name.username
    posts_db = Post.find({"author": username})
    post_count = posts_db.count()
    posts = []
    for post in posts_db:
        # print("posts.author " , posts['author'])
        post_user = User.get_by_id(post['author'])
        post['username'] = post_user.username
        post['image'] = post_user.image
        posts.append(post)
    return render_template('user_posts.html', user=user, posts=posts, post_count=post_count)
