import hashlib
import os
import secrets
import string
import urllib

from PIL import Image
from flask import current_app
from flask import url_for
from flask_login import current_user
from flask_mail import Message
from werkzeug.utils import secure_filename

from flaskapp import ALLOWED_EXTENSIONS, mail


def get_capitalized_name(name):
    capitalized_name = ""
    for i in name.split(" "):
        capitalized_name += i.capitalize() + " "
    return capitalized_name[:-1]


def generate_gravatar(random_string=None):
    # Set your variables here
    # email = "someone@somewhere.com"
    # default = "https://www.example.com/default.jpg"
    if not random_string:
        random_string = get_random_string()
    size = 125

    # construct the url
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(random_string.lower().encode('utf-8')).hexdigest() + "?"
    gravatar_url += urllib.parse.urlencode({'s': str(size)})
    # gravatar_url += urllib.urlencode({'d': default, 's': str(size)})

    return gravatar_url


def get_random_string(string_length=16):
    num = string_length  # define the length of the string
    # define the secrets.choice() method and pass the string.ascii_letters + string.digits as an parameters.
    res = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for x in range(num))
    # Print the Secure string with the combonation of letters, digits and punctuation
    # print("Secure random string is :" + str(res))
    return str(res)


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

