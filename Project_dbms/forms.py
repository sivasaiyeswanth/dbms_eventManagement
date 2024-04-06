from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.validators import DataRequired, Email, EqualTo

class OrganizerRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Register')

class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_type = StringField('Event Type', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Event')

class ParticipantRegistrationForm(FlaskForm):
    participant_name = StringField('Name',validators=[DataRequired()])
    college_name = StringField('College Name',validators=[DataRequired()])
    username = StringField('Username',validators=[DataRequired()])
    college_location = StringField('College Location',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class EditEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_type = StringField('Event Type', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')


class StudentLoginForm(FlaskForm):
    roll = StringField('Roll', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Student Login')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    search = StringField('Search Events', validators=[DataRequired()])
    submit = SubmitField('Search')

class StudentRegistrationForm(FlaskForm):
    roll = StringField('Roll', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    department = StringField('department', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('add_student')

class ParticipantRegistrationForm1(FlaskForm):
    participant_name = StringField('Name',validators=[DataRequired()])
    college_name = StringField('College Name',validators=[DataRequired()])
    username = StringField('Username',validators=[DataRequired()])
    college_location = StringField('College Location',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add Participant')

class LogisticsForm(FlaskForm):
    accommodation_details = StringField('Accommodation Details')
    food_cost = IntegerField('Food Cost', validators=[NumberRange(min=0)])
    submit = SubmitField('Create Logistics')

class WinnerForm(FlaskForm):
    winner_name = SelectField('Winner Name')
    submit = SubmitField('Declare Winner')