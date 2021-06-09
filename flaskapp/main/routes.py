from flask import render_template, request, Blueprint, redirect, url_for, flash
from flaskapp.models import Post
from flaskapp.config import posts_per_page
from flask_login import current_user, login_required
from flaskapp.main.forms import ContactUsForm


main_blueprint = Blueprint('main_blueprint', __name__)


@main_blueprint.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=posts_per_page)
    return render_template("main/home.html", title="Home", posts=posts)


@main_blueprint.route("/about")
def about_us():
    return render_template("main/about.html", title="About Us")


@main_blueprint.route("/contact", methods=['GET', 'POST'])
def contact_us():
    try:
        form = ContactUsForm()
        if form.validate_on_submit():
            if current_user.is_authenticated:
                if not current_user.is_email_verified:
                    flash(f"To Send Us Messages, You Must Verify Your Email", 'warning')
                    return redirect(url_for('user_blueprint.request_verify_email', email=form.email))
                else:
                    flash('Your message is sent to our team. We will shortly and surely contact you through email.','success')
                    return redirect(url_for('main_blueprint.home'))
            else:
                flash(f"To Access this Page You Must Logged In.", 'warning')
                return redirect(url_for('user_blueprint.login'))
        return render_template("main/contact.html", title="Contact Us", form=form)
    except:
        flash(f"To Access this Page You Must Verify Your Email And Logged In.", 'warning')
        return redirect(url_for('user_blueprint.login'))
