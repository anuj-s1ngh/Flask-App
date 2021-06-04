from flask import render_template, request, Blueprint
from flaskapp.models import Post


main_blueprint = Blueprint('main_blueprint', __name__)


@main_blueprint.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
    return render_template("home.html", title="Home", posts=posts)


@main_blueprint.route("/about")
def about():
    return render_template("about.html", title="About")


