from GamifiedFittness.models import *
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now
from GamifiedFittness.utils import get_object_or_none
from GamifiedFittness.constants import *

def add_goal(user, calories):
    if calories == 0:
        return {"success": False, "message": "Calories cannot be zero."}
    # get goal
    goal = get_object_or_none(Goal, user=user)
    if goal:
        return {"success": True, "message": "Goal Already Exists"}
    # add
    try:
        goal = Goal.objects.create(
            user=user,
            calories=calories,
            progress=0)
    except Exception as e:
        return {"success": False, "message": f"Error creating Goal: {str(e)}"}
    
    return {"success": True, "message": "Added Successfully"}

def update_goal_calories(user, calories):
    if calories == 0:
        return {"success": False, "message": "Calories cannot be zero."}
    # get goal
    goal = get_object_or_none(Goal, user=user)
    if not goal:
        return {"success": True, "message": "Goal not exist"}
    # update
    try:
        old_achieved_calories = goal.progress * goal.calories
        goal.calories = calories
        updated_progress = old_achieved_calories/calories
        goal.progress = round(min(updated_progress, 1.0), 5)
        goal.save()
    except Exception as e:
        return {"success": False, "message": f"Error Updating Goal: {str(e)}"}
    
    return {"success": True, "message": "Update Successfully", "data": goal}

def update_goal_progress(user, added_calories):
    # get appropiate goal
    goal = get_object_or_none(Goal, user=user)
    if not goal:
        return {"success": True, "message": "Success"}
    # Update the progress
    try:
        updated_progress = goal.progress + (added_calories/ goal.calories)
        goal.progress = round(min(updated_progress, 1.0),2)
        goal.save()
    except Exception as e:
        return {"success": False, "message": f"Error Updating Goal: {str(e)}"}
    
    return {"success": True, "message": "Updated Successfully"}