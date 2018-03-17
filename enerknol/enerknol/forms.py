from flask_security import RegisterForm as BaseRegisterForm
from flask_security.forms import Required
from wtforms import StringField


class RegisterForm(BaseRegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    user_name = StringField('User Name', [Required()])
