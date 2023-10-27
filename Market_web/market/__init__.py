from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)


# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

# to secure forms
app.config['SECRET_KEY'] = 'bd60671d944f3bfe05748e88'

# initialise the database
db = SQLAlchemy(app)

# allows us to create the models
app.app_context().push()

# allows us to hash password
bcrypt = Bcrypt(app)

# config of the login
login_manager = LoginManager(app)

# setting the login or the page (login_required) that a user should be directed when he/she is not login
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'


# it should always be down
from market import routes