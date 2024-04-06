from flask import Flask, render_template, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from forms import *
import secrets
import os
from sqlalchemy import func
from sqlalchemy import event
from forms import OrganizerRegistrationForm, EventForm, ParticipantRegistrationForm, EditEventForm, StudentLoginForm, LoginForm, SearchForm, StudentRegistrationForm,ParticipantRegistrationForm1, LogisticsForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:nprv@localhost:5432/dbms'
app.config['SECRET_KEY'] = secrets.token_hex(16)
db = SQLAlchemy(app)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(100), nullable=False)
    college_location = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Student(db.Model):
    roll = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Organiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    # events = db.relationship('Organiser_Event', backref='organiser', cascade='all, delete-orphan')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    over = db.Column(db.Boolean, nullable=False, default=False)

    # organiser_id = db.Column(db.Integer, db.ForeignKey('organiser.id'), nullable=False)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.Integer,db.ForeignKey('student.roll'),nullable=False)
    event_id = db.Column(db.Integer,db.ForeignKey('event.id'),nullable=False)

class Organiser_Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organiser_id = db.Column(db.Integer, db.ForeignKey('organiser.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


class Participant_Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class Student_Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.Integer, db.ForeignKey('student.roll'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False,primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False,primary_key=True)

class EventDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), unique=True, nullable=False)
    accommodation_details = db.Column(db.Text, nullable=True)
    food_cost = db.Column(db.Float, nullable=True)

#model for admin
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


# Function to create the 'organiser', 'event', and 'organiser_event' tables
# def create_tables():
with app.app_context():
    # Create all tables
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student_home', methods=['GET', 'POST'])
def student_home():
    student_roll = session.get('student_roll')
    student = Student.query.get(student_roll)
    if student:
        student = Student.query.get(student_roll)

        # Retrieve all events
        all_events = db.session.query(Event).all()

        volunteered_events = db.session.query(Event).join(Volunteer).filter(Volunteer.roll == student_roll).all()

        # Retrieve registered events for the student
        registered_events = db.session.query(Event).join(Student_Event).filter(Student_Event.roll == student_roll).all()

        # Calculate available events by excluding registered events
        available_events = [event for event in all_events if event not in registered_events]

        available_events_not_volunteered = [event for event in available_events if event not in volunteered_events]

        return render_template('student_home.html', student=student, all_events=all_events,available_events_not_volunteered=available_events_not_volunteered, registered_events=registered_events, volunteered_events=volunteered_events)
    # else:
        # Redirect to login if student is not logged in
    return redirect(url_for('login'))

@app.route('/volunteer_register/<int:student_roll>/<int:event_id>', methods=['GET','POST'])
def volunteer_register(student_roll,event_id):
    student_id = session.get('student_roll')
    if student_id != student_roll:
        return redirect(url_for('login'))
    volunteer = Volunteer(
        roll = student_roll,
        event_id = event_id
    )

    db.session.add(volunteer)
    db.session.commit()
    return redirect(url_for('student_home'))

@app.route('/event_register/<int:student_roll>/<int:event_id>', methods=['GET', 'POST'])
def event_register(student_roll,event_id):
    student_id = session.get('student_roll')
    if student_id != student_roll:
        return redirect(url_for('login'))
    student_event = Student_Event(
        roll = student_roll,
        event_id = event_id
    )

    db.session.add(student_event)
    db.session.commit()
    return redirect(url_for('student_home'))

@app.route('/event_deregister_student/<int:student_roll>/<int:event_id>', methods=['GET', 'POST'])
def event_deregister_student(student_roll,event_id):
    student_id = session.get('student_roll')
    if student_id != student_roll:
        return redirect(url_for('login'))
    student_event = Student_Event.query.filter_by(roll = student_roll,event_id = event_id).first()
    db.session.delete(student_event)
    db.session.commit()
    return redirect(url_for('student_home'))

@app.route('/volunteer_deregister_student/<int:student_roll>/<int:event_id>', methods=['GET', 'POST'])
def volunteer_deregister_student(student_roll,event_id):
    student_id = session.get('student_roll')
    if student_id != student_roll:
        return redirect(url_for('login'))
    volunteer = Volunteer.query.filter_by(roll = student_roll,event_id = event_id).first()
    db.session.delete(volunteer)
    db.session.commit()
    return redirect(url_for('student_home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form1 = StudentLoginForm()
    form2 = LoginForm()
    if form2.validate_on_submit():
        username = form2.username.data
        password = form2.password.data

        organiser = Organiser.query.filter_by(username=username, password=password).first()

        if organiser:
            # Login successful, store organiser details in session
            session['organiser_id'] = organiser.id
            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('organiser_home'))

        participant = Participant.query.filter_by(username=username, password=password).first()

        if participant:
            # Login successful, store organiser details in session
            session['participant_id'] = participant.id
            # organiser id and details
            # events = db.session.query(Event, Organiser).join(Organiser).all()

            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('participant_home'))
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            # Login successful, store organiser details in session
            session['admin_id'] = admin.id
            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('admin_home'))

        else:
            flash('Login unsuccessful. Check your username and password.', 'danger')

    if form1.validate_on_submit():
        roll = form1.roll.data
        password = form1.password.data
        student = Student.query.filter_by(roll=roll,password=password).first()

        if student:
            session['student_roll'] = student.roll
            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('student_home'))

    return render_template('login.html', form1=form1, form2=form2)

@app.route('/logout/<int:_id>',methods=['GET','POST'])
def logout(_id):
    session.pop('organiser_id', '_id')   
    # session.pop('participant_id', None)
    # session.pop('student_roll', None)
    return redirect(url_for('login'))

@app.route('/logout_participant/<int:_id>', methods=['GET', 'POST'])
def logout_participant(_id):
    session.pop('participant_id', '_id')
    return redirect(url_for('login'))

@app.route('/logout_student/<int:_id>', methods=['GET', 'POST'])
def logout_student(_id):
    session.pop('student_roll', '_id')
    return redirect(url_for('login'))

@app.route('/logout_admin/<int:_id>', methods=['GET', 'POST'])
def logout_admin(_id):
    session.pop('admin_id', '_id')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def confirm_organiser_registration():
    return render_template('register.html')


@app.route('/organiser_register', methods=['GET', 'POST'])
def organiser_register():
    form = OrganizerRegistrationForm()
    if form.validate_on_submit():
        # Create a new organiser based on the form data and add it to the database
        new_organiser = Organiser(
            username=form.username.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(new_organiser)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('organiser_register.html', form=form)

@app.route('/organiser_home', methods=['GET', 'POST'])
def organiser_home():
    organiser_id = session.get('organiser_id')
    organiser = Organiser.query.get(organiser_id)
    if organiser:
        # organiser = Organiser.query.get(organiser_id)

        # Initialize the search form
        search_form = SearchForm()
        matching_events = []
        # Handle form submission for search
        if search_form.validate_on_submit():
            search_query = search_form.search.data
            # Perform the search based on the search_query
            matching_events = Event.query.filter(
                
                Event.event_name.ilike(f'%{search_query}%')
            ).all()

            return render_template('search_results_for_org.html', organiser=organiser, events=matching_events,length = len(matching_events),search_form=search_form)

        # If not a form submission, retrieve all events held by the organiser
        events_held_by_organiser = db.session.query(Event).join(Organiser_Event).filter(Organiser_Event.organiser_id == organiser_id).all()


        return render_template('organiser_home.html', organiser=organiser, events_held_by_organiser=events_held_by_organiser, search_form=search_form)
    else:
        # Redirect to login if organiser is not logged in
        return redirect(url_for('login'))


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = EventForm()
    new_event = None  # Define new_event outside the block
    organiser = None  # Initialize organiser outside the block
    organiser_id = session.get('organiser_id')  # Get organiser_id from the session
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return redirect(url_for('login'))
    if form.validate_on_submit():
        existing_event = Event.query.filter(func.lower(Event.event_name) == func.lower(form.event_name.data)).first()
        if existing_event:
            flash('Event name already exists. Please choose a different name.', 'danger')
            return render_template('create_event.html', form=form)
        # If the organiser is found, set the organiser_id for the new event
        new_event = Event(
            event_name=form.event_name.data,
            event_type=form.event_type.data,
            date=form.date.data,
            time=form.time.data,
            venue=form.venue.data,
            description=form.description.data,
            # organiser_id=organiser.id  # Set organiser_id
        )

        db.session.add(new_event)
        db.session.commit()
        organiser_event = Organiser_Event(organiser_id=organiser_id, event_id=new_event.id)
        db.session.add(organiser_event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('organiser_home'))
    return render_template('create_event.html', form=form)
    

@app.route('/search_events', methods=['POST'])
def search_events():
    organiser_id = session.get('organiser_id')  # Get organiser_id from the session
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return redirect(url_for('login'))
    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.search.data
        # Perform the search based on the search_query
        # You need to implement the search logic based on your requirements

        # For now, let's assume you have a list of events matching the query
        matching_events = Event.query.filter(Event.event_name.ilike(f'{search_query}')).all()

        return render_template('search_results.html', events=matching_events)

    return redirect(url_for('organiser_home'))

@app.route('/event_details_student/<int:event_id>')
def event_details_student(event_id):
    student_roll = session.get('student_roll')
    if student_roll:
        organiser_event = Organiser_Event.query.filter_by(event_id=event_id).first()
        organiser = Organiser.query.filter_by(id=organiser_event.organiser_id).first()
        event_details = EventDetails.query.filter_by(event_id=event_id).first()
        event = Event.query.get(event_id)
        return render_template('event_details_student.html', event=event,event_details=event_details, organiser=organiser)
    else:
        return redirect(url_for('login'))

@app.route('/event_details_organiser/<int:event_id>')
def event_details_organiser(event_id):
    organiser_id = session.get('organiser_id')
    if organiser_id:
        organiser_event = Organiser_Event.query.filter_by(event_id=event_id).first()
        organiser = Organiser.query.filter_by(id=organiser_event.organiser_id).first()
        event_details = EventDetails.query.filter_by(event_id=event_id).first()
        event = Event.query.get(event_id)
        return render_template('event_details_organiser.html', event=event,event_details=event_details, organiser=organiser)
    else:
        return redirect(url_for('login'))
    
@app.route('/event_details_participant/<int:event_id>')
def event_details_participant(event_id):
    participant_id = session.get('participant_id')
    if participant_id:
        organiser_event = Organiser_Event.query.filter_by(event_id=event_id).first()
        organiser = Organiser.query.filter_by(id=organiser_event.organiser_id).first()
        event_details = EventDetails.query.filter_by(event_id=event_id).first()
        event = Event.query.get(event_id)
        return render_template('event_details_participant.html', event=event,event_details=event_details, organiser=organiser)
    else:
        return redirect(url_for('login'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    organiser_id = session.get('organiser_id')  # Get organiser_id from the session
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return redirect(url_for('login'))
    event = Event.query.get(event_id)

    if event and organiser:
        organiser_event = Organiser_Event.query.filter_by(organiser_id=organiser.id, event_id=event.id).first()
        if organiser_event:
            form = EditEventForm(obj=event)
            if form.validate_on_submit():
                # Update event details in the database
                event.event_name = form.event_name.data
                event.event_type = form.event_type.data
                event.date = form.date.data
                event.time = form.time.data
                event.venue = form.venue.data
                event.description = form.description.data
                db.session.commit()

                flash('Event updated successfully!', 'success')
                return redirect(url_for('organiser_home'))

            return render_template('edit_event.html', form=form, event=event)
    
    flash("You don't have access to edit this event.", 'danger')
    return redirect(url_for('organiser_home'))

@app.route("/participate_register", methods=['GET', 'POST'])
def participate_register():
    form = ParticipantRegistrationForm()

    if form.validate_on_submit():
        # Check if the username already exists
        existing_user = Participant.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('participate_register'))

        existing_user = Organiser.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('participate_register'))
        if form.password.data != form.confirm_password.data:
            flash('confirm password didnt matched with password.', 'error')
            return redirect(url_for('participate_register'))
        new_participant = Participant(
            participant_name=form.participant_name.data,
            college_name=form.college_name.data,
            college_location=form.college_location.data,
            username=form.username.data,
            password=form.password.data
        )

        db.session.add(new_participant)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('participant_register.html', title='Register', form=form)

@app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():
    # fetch admin_id from session
    admin_id = session.get('admin_id')
    if admin_id:
        admin = Admin.query.get(admin_id)
        # admin must have the access to remove or add any user

        return render_template('admin_home.html', admin_id=admin_id)
    
    return redirect(url_for('login'))

@app.route('/view_students', methods=['GET', 'POST'])
def view_students():
    admin_id = session.get('admin_id')
    if admin_id:
        students = Student.query.all()
        return render_template('view_students.html', students=students)
    return redirect(url_for('login'))

@app.route('/view_participants', methods=['GET', 'POST'])
def view_participants():
    admin_id = session.get('admin_id')
    if admin_id:
        participants = Participant.query.all()
        return render_template('view_participants.html', participants=participants)
    return redirect(url_for('login'))

@app.route('/view_organisers', methods=['GET', 'POST'])
def view_organisers():
    admin_id = session.get('admin_id')
    if admin_id:
        organisers = Organiser.query.all()
        return render_template('view_organisers.html', organisers=organisers)
    return redirect(url_for('login'))

@app.route('/remove_student/<int:roll>', methods=['GET', 'POST'])
def remove_student(roll):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    if admin:
        student = Student.query.get(roll)
        all_rows = db.session.query(Student_Event).filter_by(roll=roll).all()
        for row in all_rows:
            db.session.delete(row)
        all_rows = db.session.query(Volunteer).filter_by(roll=roll).all()
        for row in all_rows:
            db.session.delete(row)
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('view_students'))
    return redirect(url_for('login'))

@app.route('/remove_participant/<int:id>', methods=['GET', 'POST'])
def remove_participant(id):
    admin_id = session.get('admin_id')
    if admin_id:
        participant = Participant.query.get(id)
        all_rows = db.session.query(Participant_Event).filter_by(participant_id=id).all()
        for row in all_rows:
            db.session.delete(row)
        db.session.delete(participant)
        db.session.commit()
        return redirect(url_for('view_participants'))
    return redirect(url_for('login'))



@app.route('/remove_organiser/<int:id>', methods=['GET', 'POST'])
def remove_organiser(id):
    admin_id = session.get('admin_id')
    if admin_id:
        organiser = Organiser.query.get(id)
        all_rows = db.session.query(Organiser_Event).filter_by(organiser_id=id).all()
        event_ids = [row.event_id for row in all_rows]
        for row in all_rows:
            db.session.delete(row)
        for event_id in event_ids:
            remaining_rows = db.session.query(Organiser_Event).filter_by(event_id=event_id).all()
            if not remaining_rows:
                event = db.session.query(Event).filter_by(id=event_id).first()
                if event:
                    db.session.delete(event)
        # print("delete organiser")
        db.session.delete(organiser)
        db.session.commit()
        # print("deleted")
        return redirect(url_for('view_organisers'))
    return redirect(url_for('login'))

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    if not admin:
        return redirect(url_for('login'))
    form = StudentRegistrationForm()
    
    if form.validate_on_submit():
        existing_student = Student.query.filter_by(roll=form.roll.data).first()
        if existing_student:
            flash('Username already exists. Please choose a different roll.', 'error')
            return redirect(url_for('add_student'))
        print(form.roll.data, form.name.data, form.department.data, form.username.data, form.password.data)
        new_student = Student(
            roll=form.roll.data,
            student_name=form.name.data,
            dept_name=form.department.data,
            username=form.username.data,
            password=form.password.data
        )

        db.session.add(new_student)
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('view_students'))

    return render_template('add_student.html',  form=form)

@app.route('/add_organiser', methods=['GET', 'POST'])
def add_organiser():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    if not admin:
        return redirect(url_for('login'))
    form = OrganizerRegistrationForm()
    if form.validate_on_submit():
        existing_organiser = Organiser.query.filter_by(username=form.username.data).first()
        existing_participant = Participant.query.filter_by(username=form.username.data).first()
        if existing_organiser or existing_participant:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('add_organiser'))

        new_organiser = Organiser(
            username=form.username.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )

        db.session.add(new_organiser)
        db.session.commit()

        flash('Organiser added successfully!', 'success')
        return redirect(url_for('view_organisers'))
    return render_template('add_organiser.html', form=form)

@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    if not admin:
        return redirect(url_for('login'))
    form = ParticipantRegistrationForm1()
    # print(1000)
    if form.validate_on_submit():
        # print(10000);
        existing_participant = Participant.query.filter_by(username=form.username.data).first()
        existing_organiser = Organiser.query.filter_by(username=form.username.data).first()
        if existing_participant or existing_organiser:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('add_participant'))

        new_participant = Participant(
            participant_name=form.participant_name.data,
            college_name=form.college_name.data,
            college_location=form.college_location.data,
            username=form.username.data,
            password=form.password.data
        )

        db.session.add(new_participant)
        db.session.commit()
        # print("created")
        flash('Participant added successfully!', 'success')
        return redirect(url_for('view_participants'))
    return render_template('add_participant.html', form=form)

# Siva code

@app.route('/participant_home', methods=['GET', 'POST'])
def participant_home():
    participant_id = session.get('participant_id')
    # participant = Participant(participant_id=participant_id)
    if not participant_id:
        return redirect(url_for('login'))
    if participant_id:
        events = Event.query.all()
        participant = Participant.query.get(participant_id)

        # Initialize the search form
        search_form = SearchForm()
        all_events = db.session.query(Event).all()

        # Retrieve registered events for the student
        registered_events = db.session.query(Event).join(Participant_Event).filter(Participant_Event.participant_id == participant_id).all()

        # Calculate available events by excluding registered events
        available_events = [event for event in all_events if event not in registered_events]

        
        # Handle form submission for search
        if search_form.validate_on_submit():
            search_query = search_form.search.data
            # Perform the search based on the search_query
            matching_events = Event.query.filter(
                
                Event.event_name.ilike(f'%{search_query}%')
            ).all()

            # If there's exactly one matching event, redirect to its details page
            # if matching_events:
                
            return render_template('search_results_forp.html', events=matching_events, length=len(matching_events))

            
            # else:
            # # If there are multiple matching events or none, display the search results
            #     return render_template('participant_home.html',participant_id=participant_id,participant=participant, matching_events=matching_events, available_events=available_events, registered_events=registered_events,search_form=search_form,events=all_events)

        matching_events = []
        return render_template('participant_home.html', participant_id=participant_id,participant=participant, available_events=available_events, registered_events=registered_events,search_form=search_form,events=events,matching_events=matching_events)
        
    else:
        # Redirect to login if organiser is not logged in
        return redirect(url_for('login'))

@app.route('/deregister_forp/<int:participant_id>/<int:event_id>', methods=['GET', 'POST'])
def deregister_forp(participant_id, event_id):
    participant_id = session.get('participant_id')
    # participant = Participant(participant_id=participant_id)
    if not participant_id:
        return redirect(url_for('login'))
    # Assuming your Participant_Event model is named Participant_Event
    participant_event = Participant_Event.query.filter_by(participant_id=participant_id, event_id=event_id).first()

    if participant_event:
        db.session.delete(participant_event)
        db.session.commit()
        flash('Successfully deregistered from the event.', 'success')
    else:
        flash('You are not registered for this event.', 'danger')

    return redirect(url_for('participant_home'))

@app.route('/event_register_forp/<int:participant_id>/<int:event_id>', methods=['GET', 'POST'])
def event_register_forp(participant_id,event_id):
    participant_id = session.get('participant_id')
    # participant = Participant(participant_id=participant_id)
    if not participant_id:
        return redirect(url_for('login'))
    existing_registration = Participant_Event.query.filter_by(
        participant_id=participant_id,
        event_id=event_id
    ).first()

    if existing_registration:
        # Participant is already registered, flash a message
        flash('You are already registered for this event.', 'warning')
    else:
        # Participant is not registered, proceed with the insertion
        participant_event = Participant_Event(
            participant_id=participant_id,
            event_id=event_id
        )

        db.session.add(participant_event)
        db.session.commit()
        flash('Registration successful!', 'success')

    return redirect(url_for('participant_home'))

@app.route('/event_details_forp/<int:event_id>')
def event_details_forp(event_id):
    participant_id = session.get('participant_id')
    # participant = Participant(participant_id=participant_id)
    if not participant_id:
        return redirect(url_for('login'))
    event = Event.query.get(event_id)
    event_details = EventDetails.query.filter_by(event_id=event_id).first()
    return render_template('event_details_forp.html', event=event, event_details=event_details)

@app.route('/create_logistics/<int:event_id>', methods=['GET', 'POST'])
def create_logistics(event_id):
    organiser_id = session.get('organiser_id')  # Get organiser_id from the session
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return redirect(url_for('login'))
    form = LogisticsForm()
    event = Event.query.get(event_id)

    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('organiser_home'))

    if form.validate_on_submit():
        event_details = EventDetails.query.filter_by(event_id=event.id).first()
        if event_details:
            flash('Logistics already created for this event', 'danger')
            return redirect(url_for('organiser_home'))
        event_details = EventDetails(
            event_id=event.id,
            accommodation_details=form.accommodation_details.data,
            food_cost=form.food_cost.data
        )
        db.session.add(event_details)
        db.session.commit()

        flash('Logistics created successfully!', 'success')
        return redirect(url_for('organiser_home'))

    return render_template('create_logistics.html', form=form)

@app.route('/declare_winner/<int:event_id>', methods=['GET', 'POST'])
def declare_winner(event_id):
    organiser_id = session.get('organiser_id')  # Get organiser_id from the session
    organiser = Organiser.query.get(organiser_id)
    if not organiser:
        return redirect(url_for('login'))
    form = WinnerForm()

    # Convert event_id to integer
    event_id = int(event_id)

    # Get the event for which the organizer is declaring winners
    event = Event.query.get(event_id)

    # Get participant and student names for the specified event
    participant_names = db.session.query(Participant.participant_name).join(Participant_Event).filter_by(event_id=event_id).all()
    student_names = db.session.query(Student.student_name).join(Student_Event).filter_by(event_id=event_id).all()

    # Combine participant and student names into a single list
    all_names = participant_names + student_names

    # Populate the dropdown list in the form
    form.winner_name.choices = [(name, name) for name, in all_names]

    if form.validate_on_submit():
        winner_name = form.winner_name.data

        # Check if the winner has already been declared for this event
        existing_winner = Winner.query.filter_by(name=winner_name, event_id=event_id).first()

        if existing_winner:
            flash('Participant has already been declared a winner for this event', 'warning')
        else:
            # Add the winner to the database
            winner = Winner(name=winner_name, event_id=event_id)
            db.session.add(winner)
            
            event = Event.query.get(event_id)
            event.over = True
            db.session.commit()
            flash('Winner declared successfully', 'success')
            return redirect(url_for('organiser_home'))

    return render_template('declare_winner.html', form=form, event=event, participants=all_names)

@app.route('/see_winners/<int:event_id>', methods=['GET'])

def see_winners(event_id):
    participant_id = session.get('participant_id')
    # participant = Participant.(id=participant_id)
    if not participant_id:
        return redirect(url_for('login'))
    # Fetch the winners for the specified event from the Winner table
    winners = Winner.query.filter_by(event_id=event_id).all()

    # Fetch the event details for display
    event = Event.query.get(event_id)

    return render_template('see_winners.html', event=event, winners=winners)


if __name__ == "__main__":
    # create_tables()
    app.run(debug=True)