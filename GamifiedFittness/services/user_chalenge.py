from GamifiedFittness.models import *
from GamifiedFittness.utils import get_object_or_none
from django.db.models import Sum, F, Count, ExpressionWrapper, FloatField
from django.db.models import DateField
from django.db.models.functions import Cast
from django.db import transaction
from .user_goal import *

from django.forms.models import model_to_dict

def serialize_user_challenge(user_challenge):
    return {
        'id': user_challenge.id,
        'progress': user_challenge.progress,
        'points_earned': user_challenge.points_earned,
        'challenge': model_to_dict(user_challenge.challenge, exclude=['participants']),
        'user': model_to_dict(user_challenge.user, fields=['id', 'username', 'email']),
    }

@transaction.atomic
def edit_user_chalenge(user, challenge_id, progress):
    # load Challenge
    challenge = get_object_or_none(Challenge, id=challenge_id)
    if not challenge:
        return {"success": False, "message": "Chalenge Not Found"}
    user_challenge = get_object_or_none(UserChallenge,  user=user, challenge=challenge)
    if not user_challenge:
        return {"success": False, "message": "Chalenge Not Found"}   
    # Update 
    old_calories = challenge.calories * user_challenge.progress
    try:
        user_challenge.progress = progress
        user_challenge.points_earned = progress * challenge.points
        user_challenge.save()
    except Exception as e:
        return {"success": False, "message": "Could not be Updated"}   
    # Goal
    new_calories = challenge.calories * progress
    added_calories = new_calories - old_calories
    rslt = update_goal_progress(user, added_calories)
    if not rslt.get("success", False):
        return {"success": False, "message": rslt.get("message", "error")}
    
    return {"success": True, 'message': 'Updated successfully!'} 


def get_challenge_summary(user):
    # user challenge summary (total points, count of chalenges, and points per day)
    user_challenges_summary = (
        UserChallenge.objects.filter(user=user)
        .annotate(start_date_truncated=Cast('challenge__start_date', DateField()),
        calories=ExpressionWrapper(
            F('progress') * F('challenge__calories'), output_field=FloatField()
        ))
        .values('start_date_truncated')  # Group by start date
        .annotate(
            points=Sum('points_earned'),  # Sum points for day
            calories=Sum('calories'),  # Sum total_calories for the day
            count=Count('id')    # Count the challenges per day
        )
        .order_by('start_date_truncated') 
    )
    # points per day
    formatted_points_per_day = [
        {"date": day_summary["start_date_truncated"].strftime('%Y-%m-%d'), "points": day_summary["points"], "calories": day_summary["calories"]}
        for day_summary in user_challenges_summary
    ]

    # total points and count of activities
    total_points = sum(day_summary["points"] for day_summary in user_challenges_summary)
    total_calories = sum(day_summary["calories"] for day_summary in user_challenges_summary)
    count = sum(day_summary["count"] for day_summary in user_challenges_summary)

    # User Activity Summary
    user_challenge_summary = {
        "points_per_day": formatted_points_per_day,
        "count": count,
        "total_points": total_points,
        "total_calories": total_calories
    }
    
    return {"success": True, "data": user_challenge_summary}