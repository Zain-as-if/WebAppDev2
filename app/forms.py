from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange
from app.models import User

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class ReviewForm(FlaskForm):
    content = TextAreaField(validators=[InputRequired()], render_kw={"placeholder": "Write your review heree..."})
    rating = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=5)], render_kw={"placeholder": "Rating (1-5)"})
    submit = SubmitField("Submit Review")
