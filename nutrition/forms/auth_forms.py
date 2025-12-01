from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])

class MultiCheckboxField(SelectField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    
    units = SelectField('Units', choices=[
        ('metric', 'Metric (kg, cm)'),
        ('imperial', 'Imperial (lbs, ft/in)')
    ], default='metric')
    
    theme = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark')
    ], default='light')
    
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=50, max=300)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=20, max=500)])
    
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Light Activity'),
        ('moderate', 'Moderate Activity'),
        ('active', 'Very Active'),
        ('extra', 'Extra Active')
    ], default='moderate')
    
    submit = SubmitField('Save Profile')

class PreferencesForm(FlaskForm):
    activity_level = SelectField('Activity Level', choices=[
        ('sedentary', 'Sedentary'),
        ('light', 'Light Activity'),
        ('moderate', 'Moderate Activity'),
        ('active', 'Very Active'),
        ('extra', 'Extra Active')
    ], default='moderate')
    
    calorie_goal = FloatField('Daily Calorie Goal', validators=[Optional(), NumberRange(min=800, max=5000)])
    protein_goal = FloatField('Daily Protein Goal (g)', validators=[Optional(), NumberRange(min=20, max=300)])
    carb_goal = FloatField('Daily Carb Goal (g)', validators=[Optional(), NumberRange(min=50, max=800)])
    fat_goal = FloatField('Daily Fat Goal (g)', validators=[Optional(), NumberRange(min=20, max=200)])
    
    dietary_preferences = MultiCheckboxField('Dietary Preferences', choices=[
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Ketogenic'),
        ('paleo', 'Paleo'),
        ('mediterranean', 'Mediterranean'),
        ('halal', 'Halal'),
        ('kosher', 'Kosher'),
        ('gluten_free', 'Gluten-Free'),
        ('dairy_free', 'Dairy-Free')
    ])
    
    allergies = TextAreaField('Allergies & Food Restrictions', 
                             render_kw={'placeholder': 'List any food allergies or restrictions...'})
    
    health_goals = MultiCheckboxField('Health Goals', choices=[
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Weight Maintenance'),
        ('heart_health', 'Heart Health'),
        ('diabetes_management', 'Diabetes Management'),
        ('energy_boost', 'Increase Energy'),
        ('better_sleep', 'Better Sleep'),
        ('digestive_health', 'Digestive Health')
    ])
    
    submit = SubmitField('Save Preferences')

class NotificationForm(FlaskForm):
    email_tips = BooleanField('Daily AI Tips')
    daily_tips = BooleanField('Daily AI Tips')  # Alias for email_tips
    email_reports = BooleanField('Weekly Progress Reports')
    email_goals = BooleanField('Goal Achievement Alerts')
    meal_reminders = BooleanField('Meal Reminders')
    weekly_reports = BooleanField('Weekly Progress Reports')
    goal_achievements = BooleanField('Goal Achievement Notifications')
    push_notifications = BooleanField('Push Notifications')
    push_meals = BooleanField('Push Meal Notifications')
    push_water = BooleanField('Push Water Reminders')
    push_coaching = BooleanField('AI Coaching Insights')  # From template
    sms_notifications = BooleanField('SMS Notifications')
    push_reminders = BooleanField('Push Meal Reminders')
    push_goals = BooleanField('Push Goal Alerts')
    tip_frequency = SelectField('Tip Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('never', 'Never')
    ], default='daily')  # From template
    report_frequency = SelectField('Report Frequency', choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('never', 'Never')
    ], default='weekly')  # From template
    submit = SubmitField('Save Notification Settings')

class PrivacyForm(FlaskForm):
    share_data = BooleanField('Allow anonymous data sharing for research')
    data_sharing = BooleanField('Allow anonymous data sharing for research')  # Alias for share_data
    analytics = BooleanField('Enable usage analytics')
    marketing_emails = BooleanField('Receive marketing emails')
    product_updates = BooleanField('Receive product updates')  # From error log
    public_profile = BooleanField('Make profile public')
    data_export = BooleanField('Allow data export')
    data_retention = SelectField('Data Retention', choices=[
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('5_years', '5 Years'),
        ('indefinite', 'Indefinite')
    ], default='2_years')
    profile_visibility = SelectField('Profile Visibility', choices=[
        ('private', 'Private'),
        ('friends', 'Friends Only'),
        ('public', 'Public')
    ], default='private')
    submit = SubmitField('Save Privacy Settings')

class AccountManagementForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
