from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In') 

class VideoUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[validators.Length(max=500)])
    video_file = FileField('Video File', validators=[
        FileAllowed(['mp4', 'mov', 'avi'])
    ])
    thumbnail = FileField('Thumbnail', validators=[ 
        FileAllowed(['jpg', 'jpeg', 'png'])
    ])
    submit = SubmitField('Upload Video')