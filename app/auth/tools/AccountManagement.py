from datetime import datetime, timedelta

from app.extensions import db
from app.models.account import User


#TODO FINISH THIS UP
def deactivate_inactive_accounts():
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    inactive_users = User.query.filter(User.last_request_time < one_week_ago).all()
    for user in inactive_users:
        user.active = False
        db.session.commit()
