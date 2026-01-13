from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..database import get_db
from ..models.planner import CalendarAssignment, DietAssignment
from ..models.diet_mongo import MealPlan

mobile_bp = Blueprint('mobile', __name__, url_prefix='/mobile')

@mobile_bp.route('/week')
@login_required
def week_view():
    db = get_db()
    today = datetime.now().date()
    
    # Calculate start of week (or start from today)
    # Let's show today + 6 days
    start_date = today
    dates = [start_date + timedelta(days=i) for i in range(7)]
    
    date_strs = [d.strftime('%Y-%m-%d') for d in dates]
    end_date_str = date_strs[-1]
    start_date_str = date_strs[0]
    
    # Fetch assignments
    exercise_assignments = CalendarAssignment.find_by_user_and_date_range(
        db, current_user.id, start_date_str, end_date_str
    )
    
    diet_assignments = DietAssignment.find_by_user_and_date_range(
        db, current_user.id, start_date_str, end_date_str
    )
    
    # Map assignments to dates
    days_data = []
    for d, d_str in zip(dates, date_strs):
        day_info = {
            'date': d,
            'date_str': d_str,
            'day_name': d.strftime('%A'),
            'exercise': None,
            'diet': None
        }
        
        # Find exercise for this day
        for ea in exercise_assignments:
            if ea.date_str == d_str:
                day_info['exercise'] = ea
                break
                
        # Find diet for this day
        for da in diet_assignments:
            if da.date_str == d_str:
                day_info['diet'] = da
                break
                
        days_data.append(day_info)
        
    return render_template('mobile/week_view.html', days=days_data)
