from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, PasswordField, BooleanField, IntegerField, FieldList, FormField
from wtforms.validators import Optional, DataRequired, Email, Length, EqualTo, ValidationError

from web_shop.models import User
from web_shop.utils.regex_for_country import country_regex_dict, country_list


class FilterForm(FlaskForm):

    search = StringField(label='Search', default='')
    sort = SelectField(label='Sort by', default='Newest Arrivals',
                       choices=[('A-Z', 'A-Z'), ('Z-A', 'Z-A'), ('price_decreasing', 'Price: High to Low'),
                                ('price-increasing', 'Price: Low to high'), ('Newest Arrivals', 'Newest Arrivals')])
    min_price = DecimalField(label="Min price", validators=[Optional()])
    max_price = DecimalField(label="Max price", validators=[Optional()])

    submit = SubmitField(label='Show')
    show_all = SubmitField(label='Show all')


class RegisterForm(FlaskForm):

    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(label='Confirm password', validators=[EqualTo('password'), DataRequired()])

    remember = BooleanField(label='Remember me')
    submit = SubmitField(label='Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('There already exists an account with this email. Try to log in.')


class LoginForm(FlaskForm):

    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])

    remember = BooleanField(label='Remember me')
    submit = SubmitField(label='Login')


class UpdateEmailForm(FlaskForm):

    email = StringField(label='Email', validators=[DataRequired(), Email()])
    submit = SubmitField(label='Update Email')


class LoginAdminForm(FlaskForm):

    username = PasswordField(label='username', validators=[DataRequired()])
    password = PasswordField(label='password', validators=[DataRequired()])

    submit = SubmitField(label='Login')


class AddressForm(FlaskForm):

    first_name = StringField(label='First name', validators=[Optional()])
    last_name = StringField(label='Last name', validators=[Optional()])
    street = StringField(label='Street name', validators=[DataRequired()])
    street_number = IntegerField(label="Street number", validators=[DataRequired()])
    apartment_number = IntegerField(label="Appartment number (optional)", validators=[Optional()])
    city = StringField(label="City", validators=[DataRequired()])
    country = SelectField(label="Country", choices=[(country, country) for country in country_list], default="Poland")
    postal_code = StringField(label="Postal code", validators=[DataRequired()])

    remember_address = BooleanField(label='Remember Address?', validators=[Optional()])  # unused in account page, used when finalizing transaction
    submit = SubmitField()  # no label as this form will be used in few places

    def validate_postal_code(self, postal_code):

        regex = country_regex_dict[self.country.data]
        if not regex.fullmatch(postal_code.data):
            raise ValidationError('This is not a valid postal code for your country')


class QuantityForm(FlaskForm):

    product_id = IntegerField()
    quantity = IntegerField(label='quantity')


class CartForm(FlaskForm):

    quantities = FieldList(FormField(QuantityForm))

    submit = SubmitField(label='Buy cart form')



