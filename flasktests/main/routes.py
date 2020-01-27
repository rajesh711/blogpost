from flask import render_template, request, Blueprint
from flasktests.models import User, Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    posts_db = Post.find()
    posts = []
    for post in posts_db:
        post_user = User.get_by_id_with_projection(post['author'])
        post['username'] = post_user.username
        post['image'] = post_user.image
        print(post_user.password)

        posts.append(post)
    return render_template('home.html', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
