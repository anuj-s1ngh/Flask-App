from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required

from flaskapp import bcrypt, db
from flaskapp.user.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetPasswordForm,
                                 ResetPasswordForm, RequestVerifyEmailForm, VerifyEmailForm)
from flaskapp.models import User, Post
from flaskapp.user.utils import allowed_file, save_profile_image, send_reset_password_link, send_verify_email_link

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data}.', 'success')
        return redirect(url_for('user_blueprint.request_verify_email', email=form.email.data))

    elif request.method == 'POST':
        flash(f'Account Creation Failed for {form.username.data}. Please, Try Again!', 'danger')

    return render_template("register.html", title="Register", form=form)


@user_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.is_email_verified:
                login_user(user, remember=form.remember_me.data)
                flash("Logged In Successfully.", 'success')
                next_page = request.args.get('next')
                if next_page:
                        return redirect(next_page)
                else:
                    return redirect(url_for('main_blueprint.home'))
            else:
                return redirect(url_for('user_blueprint.request_verify_email', email=form.email.data))
        else:
            flash("Invalid Credentials. Please Try Again With Valid Credentials!", 'danger')

    elif request.method == 'POST':
        flash("Invalid Credentials. Please Try Again With Valid Credentials!", 'danger')

    return render_template("login.html", title="Login", form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are Logged Out.", 'danger')
    return redirect(url_for('main_blueprint.home'))


recently_updated = False


@user_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_email_verified:
        global recently_updated
        form = UpdateAccountForm()

        if form.validate_on_submit() and ((current_user.username != form.username.data) or (current_user.email != form.email.data) or (current_user.profile_image != form.profile_image.data)):
            if form.profile_image.data and allowed_file(form.profile_image.data.filename):
                profile_image_name = save_profile_image(form.profile_image.data)
                current_user.profile_image = profile_image_name

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()

            recently_updated = True
            flash(f"Your Account has been updated Successfully.", 'success')
            return redirect(url_for('user_blueprint.account'))

        elif not recently_updated and ((current_user.username != form.username.data) or (current_user.email != form.email.data) or (current_user.profile_image != form.profile_image.data)):
            flash(f"Welcome {current_user.username}", 'success')
            recently_updated = False

        if request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            if recently_updated:
                recently_updated = False

        image_file = url_for('static', filename=f'MEDIA/IMG/PROFILE_IMG/{current_user.profile_image}')
        return render_template("account.html", title="Account", image_file=image_file, form=form)


@user_blueprint.route('/update_account', methods=['GET', 'POST'])
@login_required
def update_account():
    if current_user.is_email_verified:
        global recently_updated
        form = UpdateAccountForm()

        if form.validate_on_submit() and ((current_user.username != form.username.data) or (current_user.email != form.email.data) or (current_user.profile_image != form.profile_image.data)):
            if form.profile_image.data and allowed_file(form.profile_image.data.filename):
                profile_image_name = save_profile_image(form.profile_image.data)
                current_user.profile_image = profile_image_name

            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()

            recently_updated = True
            flash(f"Your Account has been updated Successfully.", 'success')
            return redirect(url_for('user_blueprint.account'))

        elif not recently_updated and ((current_user.username != form.username.data) or (current_user.email != form.email.data) or (current_user.profile_image != form.profile_image.data)):
            flash(f"Welcome {current_user.username}", 'success')
            recently_updated = False

        if request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            if recently_updated:
                recently_updated = False

        image_file = url_for('static', filename=f'MEDIA/IMG/PROFILE_IMG/{current_user.profile_image}')
        return render_template("account.html", title="Account", image_file=image_file, form=form)



@user_blueprint.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", title=user.username, posts=posts, user=user)


@user_blueprint.route('/request_reset_password', methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_password_link(user)
        flash('An Email Has Been Sent To Your Registered Email. Kindly Check Your Email For Further Instructions.', 'success')
        return redirect(url_for('user_blueprint.login'))
    return render_template("request_reset_password.html", title="Request Reset Password", form=form)


@user_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    user = User.verify_reset_password_token(token)

    if user is None:
        flash('That is an Invalid or Expired Token', 'warning')
        return redirect(url_for('user_blueprint.request_reset_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password Reset Successfully. You Can Login Now Using Your New Password.', 'success')
        return redirect(url_for('user_blueprint.login'))

    return render_template("reset_password.html", title="Reset Password", form=form)


@user_blueprint.route('/request_verify_email/<email>', methods=['GET', 'POST'])
def request_verify_email(email):
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    form = RequestVerifyEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_verify_email_link(user)
        flash('An Email Has Been Sent To Your Registered Email. Kindly Check Your Email For Further Instructions.', 'success')
        return redirect(url_for('user_blueprint.login'))
    if request.method == 'GET':
        form.email.data = email
    return render_template("request_verify_email.html", title="Request Verify Email", form=form)


@user_blueprint.route('/verify_email/<token>', methods=['GET', 'POST'])
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    user = User.verify_verify_email_token(token)

    if user is None:
        flash('That is an Invalid or Expired Token', 'warning')
        return redirect(url_for('user_blueprint.request_verify_email', email=""))

    form = VerifyEmailForm()
    if form.validate_on_submit():
        user.is_email_verified = True
        db.session.commit()
        flash('Your Email Verified Successfully. You Can Login Now.', 'success')
        return redirect(url_for('user_blueprint.login'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash('Your Email Verification Failed. Try Again.', 'danger')
        return redirect(url_for('user_blueprint.request_verify_email', email=user.email))

    return render_template("verify_email.html", title="Verify Email", form=form, user=user)
