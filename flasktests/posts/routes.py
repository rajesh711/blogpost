from flask import Flask, render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from flasktests.models import User, Post
from flasktests.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/posts/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_post = Post(title, content, current_user.get_id())
        new_post.save()
        flash('Your posts has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@posts.route("/posts/<string:post_id>")
def post(post_id):
    post = Post.get_by_id(post_id)
    post_user = User.get_by_id(post['author'])
    post['username'] = post_user.username
    post['image'] = post_user.image
    return render_template('post.html', post=post)


@posts.route("/posts/<string:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    delete_result = Post.delete_by_id(post_id)
    if delete_result:
        flash('Your posts has been deleted!', 'success')
    else:
        flash('Your posts not deleted!', 'info')
    return redirect(url_for('main.home'))


@posts.route("/posts/<string:post_id>/update", methods=['GET', 'POST'])
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
        flash('Your posts has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')
