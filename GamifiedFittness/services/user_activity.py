from GamifiedFittness.models import *
from django.db.models import Sum, Count
from django.db.models import DateField
from django.db.models.functions import Cast
from django.db import transaction
from django.utils.timezone import now
from GamifiedFittness.utils import get_object_or_none
from .user_goal import *
from .user_badge import *
from GamifiedFittness.constants import *

from django.forms.models import model_to_dict

def serialize_user_activity(user_activity):
    return {
        'id': user_activity.id,
        'effort': user_activity.effort,
        'points': user_activity.points,
        'calories': user_activity.calories,
        'start_date': user_activity.start_date,
        'activity': {
            'id': user_activity.activity.id,
            'name': user_activity.activity.name,
            'calories': user_activity.activity.calories,
            'points': user_activity.activity.points,
            'unit': {
                'id': user_activity.activity.unit.id,
                'name': user_activity.activity.unit.name
            }
        },
        'user': model_to_dict(user_activity.user, fields=['id', 'username', 'email']),
    }

@transaction.atomic
def create_activity(user, activity_id, effort, start_date):
        # load activity
        activity = get_object_or_none(Activity, id=activity_id)
        if not activity:
            return {"success": False, "message": "Error Loading Activity"}
        # Create UserActivity instance
        try:
            user_activity = UserActivity.objects.create(
                user=user,
                activity=activity,
                effort=int(effort),
                start_date=start_date or now()
            )
        except Exception as e:
            return {"success": False, "message": f"Error creating UserActivity: {str(e)}"}

        # Badge
        rslt = assign_badges(user)
        if not rslt.get("success", False):
            return {"success": False, "message": rslt.get("message", "error")}

        # Goal
        rslt = update_goal_progress(user, user_activity.calories)
        if not rslt.get("success", False):
            return {"success": False, "message": rslt.get("message", "error")}

        return {"success": True, "data": user_activity}


def get_activity_summary(user):
    # user acyivity summary (total points, count of activities, and points per day)
    user_activities_summary = (
        UserActivity.objects.filter(user=user)
        .annotate(start_date_truncated=Cast('start_date', DateField()))
        .values('start_date_truncated')  # Group by start date
        .annotate(
            points=Sum('points'),  # Sum points for day
            calories=Sum('calories'),  # Sum points for day
            count=Count('id')    # Count the activities per day
        )
        .order_by('start_date_truncated') 
    )
    # points per day
    formatted_points_per_day = [
        {"date": day_summary["start_date_truncated"].strftime('%Y-%m-%d'), "points": day_summary["points"], "calories": day_summary["calories"]}
        for day_summary in user_activities_summary
    ]

    # total points and count of activities
    total_points = sum(day_summary["points"] for day_summary in user_activities_summary)
    total_calories = sum(day_summary["calories"] for day_summary in user_activities_summary)
    count = sum(day_summary["count"] for day_summary in user_activities_summary)

    # User Activity Summary
    user_activity_summary = {
        "points_per_day": formatted_points_per_day,
        "count": count,
        "total_points": total_points,
        "total_calories": total_calories
    }
    return {"success": True, "data": user_activity_summary}