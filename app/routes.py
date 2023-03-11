from flask import render_template, request, redirect, url_for
# flask_login is used to manage the user sessions
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
# flask_wtf is used to create the forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, ValidationError

try:
    from app import app, db, login_manager, bcrypt
except ImportError:
    from __init__ import app, db, login_manager, bcrypt

@app.before_first_request
def create_tables():
    '''
    This function is used to create the tables in the database
    '''
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    '''
    This function is used to load the user from the database
    '''
    return User.query.get(int(user_id))

# I will use classes to store various attributes and keep track of the objects created to manage various users

# make a class for users
class User(db.Model, UserMixin):
    '''
    This class is used to create the user objects

    Attributes:
        id: the id of the user
        username: the username of the user
        password: the password of the user

    Methods:
        __repr__: returns the string representation of the object
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')" # this is the string representation of the object
    
# make a class for tasks
class Task(db.Model):
    '''
    This class is used to create the task objects

    Attributes:
        id: the id of the task
        name: the name of the task
        status: the status of the task
        user_id: the id of the user who created the task

    Methods:
        __repr__: returns the string representation of the object
    '''
    __tablename__ = 'Task'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Task('{self.name}', '{self.status}')"
    
# make a class for the registration form
class RegistrationForm(FlaskForm):
    '''
    This class is used to create the registration form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button

    Methods:
        validate_username: validates the username
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        '''
        This function is used to validate the username
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
# make a class for the login form
class LoginForm(FlaskForm):
    '''
    This class is used to create the login form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    '''
    This function is used to render the home page which is the same as the login page
    '''
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This function is used to render the login page
    '''
    # create the login form
    form = LoginForm()
    # check if the form is valid
    if form.validate_on_submit():
        # get the user from the database
        user = User.query.filter_by(username=form.username.data).first()
        # check if the user exists
        if user:
            # check if the password is correct
            if bcrypt.check_password_hash(user.password, form.password.data):
                # login the user
                login_user(user)
                # redirect to the dashboard
                return redirect(url_for('dashboard'))
        # if the user does not exist or the password is incorrect
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', form=form, error=error)
    # if the form is not valid
    else:
        return render_template('login.html', form=form)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    This function is used to render the registration page
    '''
    # create the registration form
    form = RegistrationForm()
    # check if the form is valid
    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create the user object
        user = User(username=form.username.data, password=hashed_password)
        # add the user to the database
        db.session.add(user)
        db.session.commit()
        # redirect to the login page
        return redirect(url_for('dashboard'))
    else:
        error = 'Username already exists.'
        return render_template('register.html', form=form, error=error)
    
@app.route('/dashboard')
@login_required
def dashboard():
    '''
    This function is used to render the dashboard page
    '''
    # get the tasks of the current user
    to_do = Task.query.filter_by(user_id=current_user.id, status='To Do').all()
    in_progress = Task.query.filter_by(user_id=current_user.id, status='In Progress').all()
    done = Task.query.filter_by(user_id=current_user.id, status='Done').all()
    # render the dashboard page with the tasks in corresponding columns
    return render_template('index.html', to_do=to_do, in_progress=in_progress, done=done)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    '''
    Add a task to the kanban board
    '''
    if request.method == 'POST':
        # create the task object
        task = Task(name=request.form.get("name"), status='To Do', user_id=current_user.id)
        # add the task to the database
        db.session.add(task)
        db.session.commit()
        # redirect to the dashboard
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    '''
    This function is used to logout the user
    '''
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete', methods = ['GET', 'POST'])
def delete():
    '''
    This function is used to delete a task
    '''
    if request.method == 'POST':
        # get the task from the database
        task = Task.query.filter_by(id=request.form.get("id")).first()
        # delete the task from the database
        db.session.delete(task)
        db.session.commit()
        # redirect to the dashboard
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/update_to_next', methods = ['GET', 'POST'])
def update_to_next():
    '''
    This function is used to update the status of a task
    '''
    if request.method == 'POST':
        # get the task from the database
        task = Task.query.filter_by(id=request.form.get('id')).first()
        # update the status of the task
        if task.status == 'To Do':
            task.status = 'In Progress'
        elif task.status == 'In Progress':
            task.status = 'Done'
        db.session.commit()
        # redirect to the dashboard
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/update_to_previous', methods = ['GET', 'POST'])
def update_to_previous():
    '''
    This function is used to update the status of a task
    '''
    if request.method == 'POST':
        # get the task from the database
        task = Task.query.filter_by(id=request.form.get('id')).first()
        # update the status of the task
        if task.status == 'Done':
            task.status = 'In Progress'
        elif task.status == 'In Progress':
            task.status = 'To Do'
        db.session.commit()
        # redirect to the dashboard
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('dashboard'))