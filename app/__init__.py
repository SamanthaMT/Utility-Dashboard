from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required
from models import db, User, BillingData
from auth import auth_bp
from billing import billing_bp
from dashboard import dashboard_bp

csrf = CSRFProtect()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://username:password@localhost/utility_users'
app.config['SECRET_KEY'] = 'secretkey'

db.init_app(app)
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(billing_bp, url_prefix='/billing')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)