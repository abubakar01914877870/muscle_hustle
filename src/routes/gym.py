from flask import Blueprint, render_template
from ..models.gym_mongo import Gym
from ..database import get_db

gym_bp = Blueprint('gym', __name__, url_prefix='/gyms')

@gym_bp.route('/')
def list_gyms():
    db = get_db()
    gyms = Gym.find_all(db)
    return render_template('gyms/list.html', gyms=gyms)

@gym_bp.route('/<gym_id>')
def detail(gym_id):
    db = get_db()
    gym = Gym.find_by_id(db, gym_id)
    if not gym:
        return render_template('404.html'), 404
    return render_template('gyms/detail.html', gym=gym)
