from GamifiedFittness.models import *
from django.db import transaction
from django.utils.timezone import now
from django.db.models import Q, Sum
from GamifiedFittness.utils import get_object_or_none
from GamifiedFittness.constants import *


def add_first_activity_badge(user):
        if check_badge_availability(user, BadgeType.FIRST_ACTIVITY.value):
            return {"success": True, "message": "First Activity Badge Added Succesfully"}
        
        if(UserActivity.objects.filter(user=user).count() == 1):
            first_activity_badge = get_object_or_none(Badge, id=BadgeType.FIRST_ACTIVITY.value)
            if not first_activity_badge:
                return {"success": False, "message": "First Activity Badge Not Found"}
            first_activity_user_badge = UserBadge(user=user, badge=first_activity_badge, date=now())
            try:
                first_activity_user_badge.save()   
            except Exception as e:
                return {"success": False, "message": f"Error Adding Badge: {str(e)}"}
        
        return {"success": True, "message": "First Activity Badge Added Succesfully"}

def add_run_hundred_km_badge(user):
    if check_badge_availability(user, BadgeType.RUN_HUNDRED_KM.value):
        return {"success": True, "message": "Run Hundered Km Badge Added Succesfully"}
    
    running_activity = get_object_or_none(Activity, id=ActivityType.RUNNNING.value)
    if not running_activity:
        return {"success": False, "message": "Running Activitye Not Found"}

    total_effort = UserActivity.objects.filter(user=user, activity=running_activity).aggregate(Sum('effort'))['effort__sum'] or 0
    if(total_effort >= 100):
        hundred_km_run_badge = get_object_or_none(Badge, id=BadgeType.RUN_HUNDRED_KM.value)
        if not hundred_km_run_badge:
            return {"success": False, "message": "Run Hundered Km Badge Not Found"}
        hundred_km_run_user_badge = UserBadge(user=user, badge=hundred_km_run_badge, date=now())
        try:
            hundred_km_run_user_badge.save()
        except Exception as e:
                return {"success": False, "message": f"Error Adding Badge: {str(e)}"}

    return {"success": True, "message": "Run Hundered Km Badge Added Succesfully"}

# A list of badge handler functions that are executed sequentially to assign badges to a user
BADGE_HANDLERS = [
    add_first_activity_badge,
    add_run_hundred_km_badge,
]

@transaction.atomic
def assign_badges(user):
    for handler in BADGE_HANDLERS:
        result = handler(user)
        if not result.get("success", False):
            return {"success": False, "message": result.get("message", "error")}
    
    return {"success": True, "message": "Badges Added Succesfully"}
        
def check_badge_availability(user, badge_id):
    badge = get_object_or_none(Badge, id=badge_id)
    if not badge:
        return False
    return UserBadge.objects.filter(user=user, badge=badge).exists()

