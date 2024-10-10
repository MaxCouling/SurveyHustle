from datetime import datetime, timedelta
from app import db
from app.models import Response

def delete_old_responses():
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    old_responses = Response.query.filter(Response.timestamp < one_year_ago).all()
    for response in old_responses:
        db.session.delete(response)
    db.session.commit()

delete_old_responses()