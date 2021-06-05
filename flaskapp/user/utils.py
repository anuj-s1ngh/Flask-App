import os
import secrets
from PIL import Image
from flask import url_for
from flask_login import current_user
from flask_mail import Message
from werkzeug.utils import secure_filename
from flaskapp import ALLOWED_EXTENSIONS, mail
from flask import current_app


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_image(large_image):
    output_size = (125, 125)

    img = Image.open(large_image)
    img.thumbnail(output_size)

    return img


def save_profile_image(form_image):
    random_hex = secrets.token_hex(8)

    file_name, file_extension = os.path.splitext(form_image.filename)
    file_name = secure_filename(file_name)

    new_image_name = current_user.username + "_" + file_name + "_" + random_hex + file_extension
    new_image_save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'IMG/PROFILE_IMG', new_image_name).replace('\\', '/')

    resized_form_image = resize_image(form_image)
    resized_form_image.save(new_image_save_path)

    return new_image_name


def send_reset_password_link(user):
    token = user.get_mail_token()
    msg = Message(
        subject="Password Reset Request",
        sender="dev@flaskapp",
        recipients=[user.email]
    )
    msg.body = f"""To Reset Your Password, Visit the following link:

{url_for('user_blueprint.reset_password', token=token, _external=True)}

If The Link Doesn't Work Paste In Browser And Continue.

If This Request Was Made By Mistake Or You Are The Wrong Person To Get This Mail, Then Simply Ignore.

But if You Are Right Person and This Request Was Not Made By You, Please Report Immediately.

Regards,
Developer Team at FlaskApp

Contact: dev@flaskapp
"""
    mail.send(msg)


def send_verify_email_link(user):
    token = user.get_mail_token()
    msg = Message(
        subject="Verify Email Request",
        sender="dev@flaskapp",
        recipients=[user.email]
    )
    msg.body = f"""To Verify Your Email, Visit the following link:

{url_for('user_blueprint.verify_email', token=token, _external=True)}

If The Link Doesn't Work Paste In Browser And Continue.

If You Are The Wrong Person To Get This Mail, Then Simply Ignore.

Regards,
Developer Team at FlaskApp

Contact: dev@flaskapp
"""
    mail.send(msg)


def send_change_email_link(user, new_email):
    token = user.get_mail_token()
    msg = Message(
        subject="Change Email Request",
        sender="dev@flaskapp",
        recipients=[new_email]
    )
    msg.body = f"""To Change Your Email and Verify New Email, Visit the following link:

{url_for('user_blueprint.change_email', token=token, _external=True)}

If The Link Doesn't Work Paste In Browser And Continue.

If You Are The Wrong Person To Get This Mail, Then Simply Ignore.

Regards,
Developer Team at FlaskApp

Contact: dev@flaskapp
"""
    mail.send(msg)

