from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from nutrition.extensions import db, login_manager
from nutrition.models.user import User
from nutrition.forms.auth_forms import (LoginForm, RegisterForm, ProfileForm,
                                       ForgotPasswordForm, ResetPasswordForm,
                                       PreferencesForm, NotificationForm,
                                       PrivacyForm, ChangePasswordForm)
from datetime import datetime
import json
import io

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard.index')

            flash('Welcome back!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html', form=form)

        # Create new user
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Registration successful! Welcome to Personal Nutrition AI!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user:
            token = user.generate_reset_token()
            db.session.commit()

            # In a real app, you would send an email here
            # For demo purposes, we'll show the reset link
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Password reset link (demo): {reset_url}', 'info')
        else:
            # Don't reveal if email exists or not for security
            flash('If that email is registered, you will receive a password reset link.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()

        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/profile/basic', methods=['GET', 'POST'])
@login_required
def profile_basic():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.units = form.units.data
        current_user.theme = form.theme.data
        current_user.date_of_birth = form.date_of_birth.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        current_user.activity_level = form.activity_level.data

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile_basic.html', form=form)

@auth_bp.route('/profile/preferences', methods=['GET', 'POST'])
@login_required
def profile_preferences():
    form = PreferencesForm()

    # Pre-populate form with current preferences
    if request.method == 'GET':
        form.dietary_preferences.data = current_user.get_dietary_preferences()
        form.health_goals.data = current_user.get_health_goals()
        allergies = current_user.get_allergies()
        form.allergies.data = ', '.join(allergies) if allergies else ''

    if form.validate_on_submit():
        current_user.set_dietary_preferences(form.dietary_preferences.data or [])
        current_user.set_health_goals(form.health_goals.data or [])

        # Parse allergies from text area
        allergies_text = form.allergies.data or ''
        allergies = [a.strip() for a in allergies_text.split(',') if a.strip()]
        current_user.set_allergies(allergies)

        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile_preferences.html', form=form)

@auth_bp.route('/profile/notifications', methods=['GET', 'POST'])
@login_required
def profile_notifications():
    form = NotificationForm()

    # Pre-populate form with current settings
    if request.method == 'GET':
        prefs = current_user.get_notification_preferences()
        form.daily_tips.data = prefs.get('daily_tips', True)
        form.meal_reminders.data = prefs.get('meal_reminders', True)
        form.weekly_reports.data = prefs.get('weekly_reports', True)
        form.goal_achievements.data = prefs.get('goal_achievements', True)

    if form.validate_on_submit():
        preferences = {
            'daily_tips': form.daily_tips.data,
            'meal_reminders': form.meal_reminders.data,
            'weekly_reports': form.weekly_reports.data,
            'goal_achievements': form.goal_achievements.data
        }
        current_user.set_notification_preferences(preferences)
        db.session.commit()

        flash('Notification preferences updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile_notifications.html', form=form)

@auth_bp.route('/profile/privacy', methods=['GET', 'POST'])
@login_required
def profile_privacy():
    form = PrivacyForm()

    # Pre-populate form with current settings
    if request.method == 'GET':
        settings = current_user.get_privacy_settings()
        form.data_sharing.data = settings.get('data_sharing', False)
        form.analytics.data = settings.get('analytics', True)
        form.marketing_emails.data = settings.get('marketing_emails', False)

    if form.validate_on_submit():
        settings = {
            'data_sharing': form.data_sharing.data,
            'analytics': form.analytics.data,
            'marketing_emails': form.marketing_emails.data
        }
        current_user.set_privacy_settings(settings)
        db.session.commit()

        flash('Privacy settings updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile_privacy.html', form=form)

@auth_bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Current password is incorrect', 'error')

    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/profile/export-data')
@login_required
def export_data():
    """Export user data for GDPR compliance"""
    current_user.request_data_export()
    db.session.commit()

    # Generate data export
    user_data = current_user.export_user_data()

    # Create JSON file
    json_data = json.dumps(user_data, indent=2, default=str)

    # Create file-like object
    output = io.BytesIO()
    output.write(json_data.encode('utf-8'))
    output.seek(0)

    filename = f"nutrition_ai_data_{current_user.id}_{datetime.now().strftime('%Y%m%d')}.json"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@auth_bp.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Request account deletion with 30-day grace period"""
    current_user.request_account_deletion()
    db.session.commit()

    logout_user()
    flash('Account deletion requested. You have 30 days to cancel this request.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile/cancel-deletion', methods=['POST'])
@login_required
def cancel_deletion():
    """Cancel account deletion request"""
    current_user.cancel_account_deletion()
    db.session.commit()

    flash('Account deletion cancelled successfully!', 'success')
    return redirect(url_for('auth.profile'))

