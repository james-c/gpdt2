import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm
from functools import wraps
import json
import logging
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SubmitField

class StudyApprovalForm(FlaskForm):
    submit = SubmitField('Approve')
    reject = SubmitField('Reject')

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')
csrf = CSRFProtect(app)
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mock user
class User(UserMixin):
    def __init__(self, id, is_admin=False):
        self.id = id
        self.is_admin = is_admin

    def get_id(self):
        return self.id

    def is_admin_user(self):
        return self.is_admin

# Assuming a single user for demonstration
users = {'gpdt': {'password': 'gpdt123', 'is_admin': False}, 'admin': {'password': 'admin123', 'is_admin': True}}

@login_manager.user_loader
def load_user(user_id):
    for username, user_info in users.items():
        if username == user_id:
            return User(user_id, user_info['is_admin'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Mock data for studies
studies = [
    {
        'id': 1,
        'title': 'Cardiovascular Health Initiative',
        'description': 'This study aims to explore new treatment protocols for reducing heart disease risk. It focuses on innovative medical approaches, lifestyle modifications, and preventative measures to enhance cardiovascular health. The research includes clinical trials, patient monitoring, and data analysis to identify the most effective strategies for preventing and managing heart disease.',
        'approved': False,
        'rejected': False,
        'category': 'Cardiovascular Health',
        'research_type': 'Commercial Use'
    },
    {
        'id': 2,
        'title': 'Diabetes Management and Prevention Study',
        'description': 'Investigating the effectiveness of lifestyle interventions on long-term diabetes outcomes, this study seeks to understand how diet, exercise, and behavioral changes can impact diabetes management. By following participants over several years, the study will provide insights into which interventions are most successful in controlling blood sugar levels and preventing complications associated with diabetes.',
        'approved': False,
        'rejected': False,
        'category': 'Diabetes Research',
        'research_type': 'Pharmaceutical',
        'link': 'diabetes_study_detail'
    },
    {
        'id': 3,
        'title': 'Neurodegenerative Disease Research',
        'description': 'Focused on early detection and therapeutic options for diseases like Alzheimer’s and Parkinson’s, this study aims to identify biomarkers for early diagnosis and evaluate new treatments that can slow or halt disease progression. The research includes clinical trials, brain imaging studies, and genetic analyses to develop effective therapies and improve patient outcomes.',
        'approved': False,
        'rejected': False,
        'category': 'Neurodegenerative Diseases',
        'research_type': 'Academic Research'
    },
    {
        'id': 4,
        'title': 'Mental Health and Wellness Program',
        'description': 'This program assesses the efficacy of digital therapies in managing depression and anxiety. It involves the development and testing of mobile applications and online platforms designed to provide cognitive-behavioral therapy, mindfulness training, and other mental health resources. The study measures the impact of these digital interventions on patient well-being and mental health outcomes.',
        'approved': False,
        'rejected': False,
        'category': 'Mental Health',
        'research_type': 'Commercial Use'
    },
    {
        'id': 5,
        'title': 'Cancer Genomics Study',
        'description': 'Analyzing genetic data to personalize cancer treatment and improve survival rates, this study examines the genetic mutations and variations that contribute to cancer development. By integrating genomic data with clinical outcomes, researchers aim to tailor treatments to individual patients, enhancing the effectiveness of therapies and reducing side effects.',
        'approved': False,
        'rejected': False,
        'category': 'Cancer Research',
        'research_type': 'Pharmaceutical'
    },
    {
        'id': 6,
        'title': 'Epidemiological Study on Influenza Spread',
        'description': 'Understanding patterns of flu transmission in urban areas to improve vaccination strategies, this study utilizes data from public health records, hospitals, and community surveys. The research aims to identify key factors that influence the spread of influenza, such as population density, public transportation usage, and social behaviors, to inform better prevention and vaccination policies.',
        'approved': False,
        'rejected': False,
        'category': 'Epidemiology',
        'research_type': 'Academic Research'
    },
    {
        'id': 7,
        'title': 'Geriatric Mobility Study',
        'description': 'Exploring interventions to enhance quality of life for the elderly with mobility issues, this study investigates various physical therapy techniques, assistive devices, and community programs. The goal is to identify effective strategies that improve mobility, reduce the risk of falls, and promote independence among older adults.',
        'approved': False,
        'rejected': False,
        'category': 'Geriatrics',
        'research_type': 'Commercial Use'
    },
    {
        'id': 8,
        'title': 'Infectious Disease Response Model',
        'description': 'Developing predictive models for outbreak response based on real-time data analytics, this study aims to enhance public health preparedness. By integrating data from multiple sources, such as healthcare facilities, laboratories, and environmental monitoring systems, researchers will create models that predict the spread of infectious diseases and guide effective response strategies.',
        'approved': False,
        'rejected': False,
        'category': 'Infectious Diseases',
        'research_type': 'Academic Research'
    },
    {
        'id': 9,
        'title': 'Nutritional Health Trends Project',
        'description': 'Tracking the long-term health outcomes of dietary changes across diverse populations, this project studies the impact of nutrition on chronic diseases, obesity, and overall health. The research involves large-scale surveys, dietary assessments, and longitudinal studies to understand how different eating patterns affect health outcomes over time.',
        'approved': False,
        'rejected': False,
        'category': 'Nutrition',
        'research_type': 'Commercial Use'
    }
]
# Extract categories and research types dynamically from studies
categories = {study['category'] for study in studies}
research_types = {study['research_type'] for study in studies}

# Descriptions for research types and categories
research_descriptions = {
    'Academic Research': 'Research that is openly accessible to the public and research community.',
    'Pharmaceutical': 'Research conducted by pharmaceutical companies.',
    'Commercial Use': 'Research conducted by private companies for proprietary purposes.'
}

category_descriptions = {
    'Cardiovascular': 'Studies related to heart and blood vessel health.',
    'Diabetes': 'Research focused on diabetes management and prevention.',
    'Neurodegenerative': 'Studies on diseases such as Alzheimer’s and Parkinson’s.',
    'Mental Health': 'Research on therapies and interventions for mental health.',
    'Cancer': 'Studies on genetic data to personalize cancer treatment.',
    'Epidemiology': 'Research on the spread and control of diseases.',
    'Geriatrics': 'Studies on enhancing quality of life for the elderly.',
    'Infectious Disease': 'Research on response models for disease outbreaks.',
    'Nutrition': 'Studies on the health outcomes of dietary changes.'
}

# User preferences mock data
user_preferences = {
    'meta_consent': 'case_by_case',
    'research_types': [],
    'categories': [],
    'specific_projects': []
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info(f"Form CSRF Token: {request.form.get('csrf_token')}")
    logging.info(f"Session CSRF Token: {session.get('_csrf_token')}")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password:
            user = User(username, users[username]['is_admin'])
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin_user():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
@admin_login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/study_approvals')
@admin_login_required
def study_approvals():
    # This would list all studies awaiting approval
    return render_template('study_approvals.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def update_user_preferences(user_id, preferences):
    user_preferences['research_use'] = preferences.get('researchUse', {})
    user_preferences['specific_projects'] = preferences.get('specificProjects', {})

def apply_meta_consent(meta_consent):
    if meta_consent == 'allow-all':
        for category in categories:
            user_preferences['research_use'][category] = True
        for study in studies:
            user_preferences['specific_projects'][study['id']] = True
    elif meta_consent == 'deny-all':
        for category in categories:
            user_preferences['research_use'][category] = False
        for study in studies:
            user_preferences['specific_projects'][study['id']] = False

@app.route('/data-preferences', methods=['GET', 'POST'])
@login_required
def data_preferences():
    if 'user_preferences' not in session:
        session['user_preferences'] = {
            'meta_consent': 'case-by-case',
            'research_types': [],
            'categories': [],
            'specific_projects': []
        }

    user_preferences = session['user_preferences']
    logging.info('User preferences session loaded: %s', session)

    if request.method == 'POST':
        user_preferences['meta_consent'] = request.form.get('metaConsent')
        user_preferences['research_types'] = request.form.getlist('researchTypes')
        user_preferences['categories'] = request.form.getlist('categories')
        user_preferences['specific_projects'] = request.form.getlist('specificProjects')

        session['user_preferences'] = user_preferences
        logging.info('User preferences saved: %s', user_preferences)

        return redirect(url_for('dashboard'))

    approved_studies = [study for study in studies if study['approved']]
    research_types = list(set(study['research_type'] for study in studies))
    categories = list(set(study['category'] for study in studies))

    return render_template('data_preferences.html',
                           meta_consent=user_preferences['meta_consent'],
                           research_types=research_types,
                           categories=categories,
                           user_preferences=user_preferences,
                           approved_studies=approved_studies)

@app.route('/activity-log')
@login_required
def activity_log():
    return render_template('activity_log.html')

@app.route('/governance-info')
@login_required
def governance_info():
    return render_template('governance_info.html')

@app.route('/audit')
@login_required
def audit():
    return render_template('audit.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register/step1', methods=['GET', 'POST'])
def register_step1():
    if request.method == 'POST':
        return redirect(url_for('register_step2'))
    return render_template('register_step1.html')

@app.route('/register/step2', methods=['GET', 'POST'])
def register_step2():
    if request.method == 'POST':
        return redirect(url_for('register_step3'))
    return render_template('register_step2.html')

@app.route('/register/step3', methods=['GET'])
def register_step3():
    return render_template('register_step3.html')

@app.route('/register/step4', methods=['GET', 'POST'])
def register_step4():
    if request.method == 'POST':
        return redirect(url_for('register_step5'))
    return render_template('register_step4.html')

@app.route('/register/step5', methods=['GET', 'POST'])
def register_step5():
    if request.method == 'POST':
        return redirect(url_for('register_step6'))
    return render_template('register_step5.html')

@app.route('/register/step6', methods=['GET', 'POST'])
def register_step6():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('register_step6.html')

def save_studies_to_session():
    session['studies'] = json.dumps(studies)

def load_studies_from_session():
    global studies
    if 'studies' in session:
        studies = json.loads(session['studies'])

@app.before_request
def load_studies():
    global studies
    session['studies'] = json.dumps(studies)

@app.route('/approve-study/<int:study_id>', methods=['POST'])
@login_required
@admin_required
def approve_study(study_id):
    load_studies_from_session()
    for study in studies:
        if study['id'] == study_id:
            study['approved'] = True
            study['rejected'] = False
            break
    save_studies_to_session()
    return redirect(url_for('admin_studies'))

@app.route('/reject-study/<int:study_id>', methods=['POST'])
@login_required
@admin_required
def reject_study(study_id):
    load_studies_from_session()
    for study in studies:
        if study['id'] == study_id:
            study['approved'] = False
            study['rejected'] = True
            break
    save_studies_to_session()
    return redirect(url_for('admin_studies'))

@app.route('/admin/studies')
@login_required
@admin_required
def admin_studies():
    form = StudyApprovalForm()
    load_studies_from_session()
    return render_template('admin_studies.html', studies=studies, form=form)

@app.route('/update-preferences', methods=['POST'])
@login_required
def update_preferences():
    user_preferences = session.get('user_preferences', {
        'meta_consent': 'case_by_case',
        'research_types': [],
        'categories': [],
        'specific_projects': []
    })
    logging.info('User preferences session: %s', session)

    user_preferences['meta_consent'] = request.form.get('metaConsent', 'case_by_case')
    user_preferences['research_types'] = request.form.getlist('researchTypes')
    user_preferences['categories'] = request.form.getlist('categories')
    user_preferences['specific_projects'] = request.form.getlist('specificProjects')

    session['user_preferences'] = user_preferences
    logging.info('User preferences saved: %s', user_preferences)

    return redirect(url_for('dashboard'))

@app.route('/diabetes-study-detail')
@login_required
def diabetes_study_detail():
    # Replace the following data with the actual details of the Diabetes Management and Prevention Study
    study_details = {
        'title': 'Diabetes Management and Prevention Study',
        'introduction': 'This study seeks to understand how diet, exercise, and behavioral changes can impact diabetes management.',
        'overview': 'By following participants over several years, the study will provide insights into which interventions are most successful in controlling blood sugar levels and preventing complications associated with diabetes.',
        'data_use': 'Your data will be used to monitor long-term outcomes and effectiveness of various lifestyle interventions.',
        'project_team': 'The project team includes leading researchers from renowned institutions.',
        'image_placeholder': 'Image of the study team or relevant graphic'
    }
    return render_template('diabetes.html', study=study_details)

if __name__ == "__main__":
    app.run(debug=True)
