from GamifiedFittness.models import *
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now
from GamifiedFittness.utils import get_object_or_none
from GamifiedFittness.constants import *

def update(user, added_calories):
    # get appropiate goal
    goal = get_object_or_none(Goal, user=user)
    if not goal:
        return {"success": True, "message": "Success"}
    # Update the progress
    updated_progress = goal.progress + (added_calories/ goal.calories)
    goal.progress = round(min(updated_progress, 1.0),2)
    goal.save()
    
    return {"success": True, "message": "Updated Successfully"}