from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from wtforms.validators import ValidationError
from flaskapp import bcrypt, db
from flaskapp.user.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetPasswordForm,
                                 ResetPasswordForm, RequestVerifyEmailForm, VerifyEmailForm, AccountForm,
                                 RequestChangeEmailForm, ChangeEmailForm, ChangePasswordForm, CloseAccountForm,
                                 EmptyForm)
from flaskapp.models import User, Post
from flaskapp.user.utils import allowed_file, save_profile_image, send_reset_password_link, send_verify_email_link, \
    send_change_email_link, get_capitalized_name

from flaskapp.config import posts_per_page
from flaskapp.user.utils import get_random_string


user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        random_identicon_string = User.generate_random_identicon_image()

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            profile_identicon_unique_string=random_identicon_string,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)

        flash(f'Account Created for {form.username.data}.', 'success')
        return redirect(url_for('user_blueprint.request_verify_email', email=form.email.data))

    elif request.method == 'POST':
        flash(f'Account creation failed for {form.username.data}. Please, Try Again!', 'danger')

    return render_template("user/register.html", title="Register", form=form)


@user_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_account_active:
                user.is_account_active = True
                db.session.commit()
                flash("Your account is activated successfully.", 'success')
            login_user(user, remember=form.remember_me.data)
            flash("You are now logged in.", 'success')
            if user.is_email_verified:
                next_page = request.args.get('next')
                if next_page:
                        return redirect(next_page)
                else:
                    return redirect(url_for('main_blueprint.home'))
            else:
                return redirect(url_for('user_blueprint.request_verify_email', email=form.email.data))
        else:
            flash("Invalid credentials, Please try again with valid credentials!", 'danger')

    elif request.method == 'POST':
        flash("Invalid credentials, Please try again with valid credentials!", 'danger')

    return render_template("user/login.html", title="Login", form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are Logged Out.", 'danger')
    return redirect(url_for('main_blueprint.home'))


@user_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_account_active:
        form = AccountForm()

        if form.validate_on_submit():
            return redirect(url_for('user_blueprint.update_account'))

        if request.method == 'GET':
            if current_user.name:
                flash(f"Welcome {current_user.name}", 'success')
            else:
                flash(f"Welcome {current_user.username}", 'success')
            form.about.data = current_user.about
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.name.data = current_user.name
            form.current_profession.data = current_user.current_profession

        image_file = url_for('static', filename=f'MEDIA/IMG/PROFILE_IMG/{current_user.profile_image}')
        return render_template("user/account.html", title="Account", image_file=image_file, form=form)

    else:
        flash(f"To access this page you must activate your account and log in.", 'warning')
        return redirect(url_for('user_blueprint.login'))


@user_blueprint.route('/account/update', methods=['GET', 'POST'])
@login_required
def update_account():
    if current_user.is_account_active:
        form = UpdateAccountForm()

        if form.validate_on_submit() and ((current_user.username != form.username.data) and (current_user.email != form.email.data) and (current_user.profile_image != form.profile_image.data)):
            return redirect(url_for('user_blueprint.account'))

        elif form.validate_on_submit() and ((current_user.username != form.username.data) or (current_user.email != form.email.data) or (current_user.profile_image != form.profile_image.data)):
            if form.profile_image.data and allowed_file(form.profile_image.data.filename):
                profile_image_name = save_profile_image(form.profile_image.data)
                current_user.profile_image = profile_image_name

            current_user.about = form.about.data
            current_user.username = form.username.data
            current_user.name = get_capitalized_name(form.name.data)
            current_user.current_profession = form.current_profession.data
            db.session.commit()

            if current_user.email != form.email.data:
                return redirect(url_for('user_blueprint.request_change_email', email=form.email.data))

            flash(f"Your Account has been updated Successfully.", 'success')
            return redirect(url_for('user_blueprint.account'))

        if request.method == 'GET':
            flash(f"You Can Update Your Account Info From Here.", 'primary')
            form.username.data = current_user.username
            form.email.data = current_user.email
            form.name.data = current_user.name
            form.current_profession.data = current_user.current_profession

        image_file = url_for('static', filename=f'MEDIA/IMG/PROFILE_IMG/{current_user.profile_image}')
        return render_template("user/update_account.html", title="Account", image_file=image_file, form=form)

    else:
        flash(f"To access this page you must activate your account and log in.", 'warning')
        return redirect(url_for('user_blueprint.login'))


@user_blueprint.route('/account/close', methods=['GET', 'POST'])
@login_required
def close_account():
    if current_user.is_authenticated:
        form = CloseAccountForm()
        user = User.query.filter_by(email=current_user.email).first()
        posts = Post.query.filter_by(author=user).all()
        if request.method == "GET":
            flash(f"Please note that after deletion of your account your all posts will also be deleted.", 'danger')
            return render_template("user/close_account.html", title="Close Account", form=form)
        elif form.validate_on_submit() and user and bcrypt.check_password_hash(user.password, form.confirm_password.data):
            if posts:
                for post in posts:
                    db.session.delete(post)
            logout_user()
            db.session.delete(user)
            db.session.commit()
            flash(f"Your Account Has Been Closed.", 'success')
            return redirect(url_for('main_blueprint.home'))
        else:
            flash(f"Invalid Password, Try Again!", 'warning')
            return render_template("user/close_account.html", title="Close Account", form=form)
    else:
        flash(f"To Access this Page You Must Logged In.", 'warning')
        return redirect(url_for('user_blueprint.login'))


@user_blueprint.route('/account/disable', methods=['GET', 'POST'])
@login_required
def disable_account():
    if current_user.is_account_active:
        current_user.is_account_active = False
        db.session.commit()
        logout_user()
        flash("Your account is disabled, you can enable it again by logging in.", "danger")
        return redirect(url_for("main_blueprint.home"))
    flash("Your account is disabled, you can enable it again by logging in.", "danger")
    return redirect(url_for("user_blueprint.login"))


@user_blueprint.route("/user/<string:username>/posts")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=posts_per_page)
    return render_template("user/user_posts.html", title=user.username, posts=posts, user=user)


@user_blueprint.route("/user/<string:username>/public_profile")
def user_public_profile(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query\
        .filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=posts_per_page)
    form = EmptyForm()
    return render_template("user/user_public_profile.html", title=user.username, posts=posts, user=user, form=form)


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
    return render_template("user/request_reset_password.html", title="Request Reset Password", form=form)


@user_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_blueprint.home'))

    user = User.verify_mail_token(token)

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

    return render_template("user/reset_password.html", title="Reset Password", form=form)


@user_blueprint.route('/request_verify_email/<email>', methods=['GET', 'POST'])
@login_required
def request_verify_email(email):
    form = RequestVerifyEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_verify_email_link(user)
        flash('An Email Has Been Sent To Your Registered Email. Kindly Check Your Email For Further Instructions.', 'success')
        return redirect(url_for('user_blueprint.login'))
    if request.method == 'GET':
        form.email.data = email
    return render_template("user/request_verify_email.html", title="Request Verify Email", form=form)


@user_blueprint.route('/verify_email/<token>', methods=['GET', 'POST'])
def verify_email(token):

    user = User.verify_mail_token(token)

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

    return render_template("user/verify_email.html", title="Verify Email", form=form, user=user)


new_email = ""
previous_email = ""


@user_blueprint.route('/request_change_email/<email>', methods=['GET', 'POST'])
@login_required
def request_change_email(email):
    global new_email, previous_email
    previous_email = current_user.email
    form = RequestChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.email.data
        user = User.query.filter_by(email=previous_email).first()
        send_change_email_link(user, new_email)
        previous_email = ""
        flash('An Email Has Been Sent To Your New Email. Kindly Check Your Email For Further Instructions.', 'success')
        return redirect(url_for('user_blueprint.account'))
    if request.method == 'GET':
        form.email.data = email
    return render_template("user/request_change_email.html", title="Request Change Email", form=form)


@user_blueprint.route('/change_email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    global new_email
    user = User.verify_mail_token(token)

    if user is None:
        flash('That is an Invalid or Expired Token', 'warning')
        return redirect(url_for('user_blueprint.request_change_email', email=""))

    form = ChangeEmailForm()
    if form.validate_on_submit():
        user.email = new_email
        db.session.commit()
        new_email = ""
        flash('Your Account Updated Successfully.', 'success')
        return redirect(url_for('user_blueprint.account'))
    elif request.method == 'POST' and not form.validate_on_submit():
        flash('Your Email Verification Failed. Try Again.', 'danger')
        return redirect(url_for('user_blueprint.request_change_email', email=user.email))

    return render_template("user/change_email.html", title="Change Email", form=form, new_email=new_email)


@user_blueprint.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user
        if user and bcrypt.check_password_hash(user.password, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash("Your Password Changed Successfully.", 'success')
            return redirect(url_for('user_blueprint.account'))
        else:
            flash("Password Change Failed, Try Again!", 'danger')

    return render_template("user/change_password.html", title="Change Password", form=form)


@user_blueprint.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.', 'danger')
            return redirect(url_for('main_blueprint.home'))
        if user == current_user:
            flash('You cannot follow yourself!', 'warning')
            return redirect(url_for('user_blueprint.user_public_profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}.', 'success')
        return redirect(url_for('user_blueprint.user_public_profile', username=username))
    else:
        return redirect(url_for('main_blueprint.home'))


@user_blueprint.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.', 'danger')
            return redirect(url_for('main_blueprint.home'))
        if user == current_user:
            flash('You cannot unfollow yourself!', 'warning')
            return redirect(url_for('user_blueprint.user_public_profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have unfollowed {username}!', 'danger')
        return redirect(url_for('user_blueprint.user_public_profile', username=username))
    else:
        return redirect(url_for('main_blueprint.home'))
