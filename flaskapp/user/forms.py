from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskapp.models import User


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=200)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=4, max=100), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken. Please, choose another username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already associated with an account.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=50)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AccountForm(FlaskForm):
    about = StringField('About', validators=[Length(min=0, max=1000)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=200)])
    name = StringField('Name', validators=[Length(min=0, max=200)])
    current_profession = StringField('Current Profession', validators=[Length(min=0, max=200)])
    submit = SubmitField('Edit Profile')


class UpdateAccountForm(FlaskForm):
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    about = StringField('About', validators=[Length(min=0, max=1000)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=200)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=200)])
    name = StringField('Name', validators=[Length(min=0, max=200)])
    choices = [
        None,
        "Student",
        "Professional",
        "Other"
    ]
    current_profession = SelectField('Current Profession', choices=choices)
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is taken. Please, choose another username.')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already associated with an account.')


class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No Account Found With This Email. You Must Register First.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=4, max=50), EqualTo('password')])
    submit = SubmitField('Reset Password')


class RequestVerifyEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    submit = SubmitField('Send Request')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No Account Found With This Email. You Must Register First.')


class VerifyEmailForm(FlaskForm):
    submit = SubmitField('Verify Email')


class RequestChangeEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=100)])
    submit = SubmitField('Send Request')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already associated with an account.')


class ChangeEmailForm(FlaskForm):
    submit = SubmitField('Change Email')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=50)])
    new_password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=50)])
    confirm_new_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=4, max=50), EqualTo('new_password')])
    submit = SubmitField('Change Password')


class CloseAccountForm(FlaskForm):
    choices = [
        "Don't Like The Platform.",
        "Privacy Concerns.",
        "Security Reasons.",
        "Want A Break.",
        "Others"
    ]
    closing_reason = SelectField('Reason For Closing Account', validators=[DataRequired()], choices=choices)
    suggestions = TextAreaField('Any Suggestions For Us', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=4, max=50)])
    submit = SubmitField('Close Account')
