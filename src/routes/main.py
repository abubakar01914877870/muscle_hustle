from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Redirect logged-in users to their dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Main User Dashboard"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('planner/dashboard.html', today_date=today_date, datetime=datetime)