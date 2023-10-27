from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, TextAreaField

# a package to validate forms
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, Optional
from market.models import User

# flask forms class <form></form>
class RegisterForm(FlaskForm):

    # flaskforms looks for any func starting by validate_ and it will look if we have any field of name username
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()

        if user:
            raise ValidationError('This Username Already exists! Please try a different username.')


    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email=email_address_to_check.data).first()

        if email_address:
            raise ValidationError(' This Email Address Already exists! Please try a different email address.')

    username = StringField(label='Username', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Adress', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6, max=30), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item!')

class PostForm(FlaskForm):
    product_name = StringField(label='Product Name', validators=[Length(min=1, max=30), DataRequired()])
    product_price = IntegerField(label='Product Price', validators=[Length(min=1, max=30), DataRequired()])
    barcode = StringField(label='Barcode', validators=[DataRequired()])
    description = TextAreaField(label='Product Description', validators=[Optional(), Length(max=200)]) 
    submit = SubmitField(label='Post')
