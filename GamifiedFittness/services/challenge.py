from GamifiedFittness.models import *
from GamifiedFittness.utils import get_object_or_none
from django.db.models import Sum
from .user_goal import *
from django.db import transaction

@transaction.atomic
def add_challenge(user, name, points, calories, start_date, end_date, description = None):
    try:
        # Add Challenge
        challenge = Challenge.objects.create(
            name=name,
            description=description,
            points=points,
            calories=calories,
            start_date=start_date,
            end_date=end_date,
        )
         
        # Add User to the Challenge
        user_challenge = UserChallenge.objects.create(
            user = user,
            challenge = challenge,
            progress = 0,
            points_earned = 0
        )
    
    except Exception as e:
        return {"success": False, "message": "Could not add"}
    
    return {"success": True, 'message': 'Added successfully!', 'data': challenge} 


