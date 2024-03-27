import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')


login_manager = LoginManager()
login_manager.init_app(app)

# Mock user
class User(UserMixin):
        def __init__(self, id):
                self.id = id

# Assuming a single user for demonstration
users = {'user1': {'password': 'password123'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to a protected dashboard page after login
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)
        
@app.route('/dashboard')
@login_required
def dashboard():
        return 'Welcome to your dashboard!'
        
@app.route('/logout')
def logout():
        logout_user()
        return redirect(url_for('login'))
                    
@app.route('/')
def index():
    return render_template('index.html')
