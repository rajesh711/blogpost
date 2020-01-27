from flask.blueprints import Blueprint
from flask.templating import render_template

from flasktests.models import User, Post

admin = Blueprint('admin', __name__)


@admin.route("/admin")
def admin1():
    user_data = User.get_all()
    users = []
    for user in user_data:
        post = Post.find({"author": str(user['_id'])})
        total_post = post.count()
        user['total'] = total_post
        users.append(user)
    return render_template('admin_panel.html', title='admin', users=users)