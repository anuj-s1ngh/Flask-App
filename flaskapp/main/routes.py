from flask import render_template, request, Blueprint
from flaskapp.models import Post
from flaskapp.config import posts_per_page


main_blueprint = Blueprint('main_blueprint', __name__)


@main_blueprint.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    return render_template("main/home.html", title="Home", posts=posts)


@main_blueprint.route("/about")
def about():
    return render_template("main/about.html", title="About")


