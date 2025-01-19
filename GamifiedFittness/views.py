from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Q, Sum
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from .models import *
from .services.leaderboard import *
from .services.statistic import *
from .services.user_activity import *
from .services.user_chalenge import *
from .services.activity import *
from .services.challenge import *
from django.forms.models import model_to_dict
from GamifiedFittness.constants import *
from django.shortcuts import redirect


# Views

## Dashboard
@login_required
def index(request):
    return render(request, "GamifiedFittness/dashboard.html")

## Login, Register, and Log out
def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is  None:
             return render(request, "GamifiedFittness/login.html", {
                "message": "Invalid username and/or password."
            })
        
        login(request, user)
        next_url = request.POST.get('next') or reverse('index')
        return redirect(next_url)

    
    return render(request, "GamifiedFittness/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "GamifiedFittness/register.html", {
                "message": "Passwords must match."
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "GamifiedFittness/register.html", {
                "message": "Username already taken."
            })
        return HttpResponseRedirect(reverse("login"))
    
    return render(request, "GamifiedFittness/register.html")


## Activity
@login_required
def list_activity_view(request):
    return render(request, 'GamifiedFittness/activity_list.html')

## Challenge
@login_required
def list_chalenge_view(request):
    return render(request, 'GamifiedFittness/chalenge_list.html')

@login_required
def challenge_view(request, challenge_id):
    return render(request, 'GamifiedFittness/challenge_view.html', {"challenge_id": challenge_id})

## Leaderboard
@login_required
def leaderboard_view(request):
    return render(request, 'GamifiedFittness/leaderboard.html')

## Statistics
def statistics_view(request):
    statistics_rslt = get_statistics()

    return render(request, 'GamifiedFittness/statistics.html', 
                  {
                      "statistics": statistics_rslt.get('data')
                  })


# Services

## Unit
def list_unit(request):
    units = Unit.objects.filter()
    units = list(units.values())  
    return JsonResponse({"success": True, 'message': 'Unit Loaded successfully!', 'units': units})

## Activity
def list_activity(request):
    activities = Activity.objects.filter()
    activities = [serialize_activity(activity) for activity in activities]
    return JsonResponse({"success": True, 'message': 'Activities Loaded successfully!', 'activities': activities})

## User Activity
@login_required
def list_user_activity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        filter = data.get('filter', None)

        name = filter.get('name') or ''
        date = filter.get('date')
    
        filter_conditions = Q(user=request.user)
        if filter and name:
            filter_conditions &= Q(activity__name__icontains=filter['name'])

        if filter and date:
            filter_conditions &= Q(start_date=filter['date'])

        # Activities
        user_activities = UserActivity.objects.filter(filter_conditions).order_by('-start_date')
        user_activities_data = [serialize_user_activity(user_activity) for user_activity in user_activities]

        return JsonResponse({"success": True, 'message': 'Activities Loaded successfully!', 'user_activities': user_activities_data})
     
    return JsonResponse({"success": False, 'message': 'Invalid request method or type.'}, status=400)

@login_required
@transaction.atomic
def add_activity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        activity = data.get('activity', None)
        activity_id = activity.get('id', 0)
        effort = activity.get('effort', 0)
        start_date = activity.get('start_date', '')

        if not activity_id or not effort or not start_date:
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)

        rslt = create_activity(request.user, activity_id, effort, start_date)
        if not rslt.get("success", False):
            return JsonResponse({"success": False, 'message': 'Could not save the activity'}, status=400)
        
        return JsonResponse({"success": True, 'message': 'Activity added successfully!', 'user_activity': model_to_dict(rslt.get('data'))})

    return JsonResponse({"success": False, 'message': 'Invalid request method or type.'}, status=400)

## Challenge
@login_required
def list_chalenges(request):
    # Chalenges
    chalenges_list = Challenge.objects.all().order_by('-start_date')
    chalenges_data = list(chalenges_list.values())  
    return JsonResponse({"success": True, 'message': 'Chalenges retrieved successfully!', 'chalenges': chalenges_data})

@login_required
def add_chalenge(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        Challenge = data.get('Challenge', None)

        name = Challenge.get('name', "")
        description = Challenge.get('description', None)
        points = Challenge.get('points', 0)
        calories = Challenge.get('calories', 0)
        start_date = Challenge.get('start_date', "")
        end_date = Challenge.get('end_date', "")

        # Validate
        if not name or not points or not calories or not start_date or not end_date:
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
        
        # Add Challenge
        challenge_rslt = add_challenge(request.user, name, points, calories, start_date, end_date, description)
        if(not challenge_rslt.get('success')):
                return JsonResponse({"success": False, 'message': 'Could not add the challenge.'}, status=400)

        return JsonResponse({"success": True, 'message': 'Challenge added successfully!'})
    
    return JsonResponse({"success": False, 'message': 'Invalid request method or type.'}, status=400)

@login_required
def load_chalenge(request, challenge_id):
    if not challenge_id:
        return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    # load Challenge
    challenge = get_object_or_none(Challenge, id=challenge_id)
    if not challenge:
        return JsonResponse({"success": False, 'message': 'Could not load the chalenge'}, status=400)
    return JsonResponse({"success": True, 'message': 'Loaded successfully!', 'challenge': model_to_dict(challenge)})  

@login_required
def join_chalenge(request, challenge_id):
    if not challenge_id:
        return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    # load Challenge
    challenge = get_object_or_none(Challenge, id=challenge_id)
    if not challenge:
        return JsonResponse({"success": False, 'message': 'Could not load the chalenge'}, status=400)
    
    user_challenge = get_object_or_none(UserChallenge,  user=request.user, challenge=challenge)
    if user_challenge:
        return JsonResponse({"success": True, 'message': 'Joined successfully!', 'user_challenge': serialize_user_challenge(user_challenge)}) 
     # Create UserChallenge instance
    try:
        user_challenge = UserChallenge.objects.create(
        user = request.user,
        challenge = challenge,
        progress = 0,
        points_earned = 0
        )
    except Exception as e:
        return JsonResponse({"success": False, 'message': 'Could not save the Challenge'}, status=400)
   
    return JsonResponse({"success": True, 'message': 'Joined successfully!', 'user_challenge': serialize_user_challenge(user_challenge)})  

@login_required
def leave_chalenge(request, challenge_id):
    if not challenge_id:
        return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    # load Challenge
    challenge = get_object_or_none(Challenge, id=challenge_id)
    if not challenge:
        return JsonResponse({"success": False, 'message': 'Could not load the chalenge'}, status=400)
    
    user_challenge = get_object_or_none(UserChallenge,  user=request.user, challenge=challenge)
    if not user_challenge:
        return JsonResponse({"success": True, 'message': 'Disconnected successfully!'}) 
    
    # Delete UserChallenge instance
    try:
        user_challenge.delete()
    except Exception as e:
        return JsonResponse({"success": False, 'message': 'Could not Disconnect from the Challenge'}, status=400)
   
    return JsonResponse({"success": True, 'message': 'Disconnected successfully!'})    

@login_required
def list_user_chalenges(request):
    # Chalenges
    user_chalenges = UserChallenge.objects.filter(user=request.user)
    user_challenges_data = [serialize_user_challenge(user_chalenge) for user_chalenge in user_chalenges]
    return JsonResponse({"success": True, 'message': 'Chalenges retrieved successfully!', 'user_chalenges': user_challenges_data})

@login_required
def load_user_chalenge(request, challenge_id):
    if not challenge_id:
        return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    # load Challenge
    user_challenge = get_object_or_none(UserChallenge, challenge_id=challenge_id, user=request.user)
    if not user_challenge:
        return JsonResponse({"success": False, 'message': 'Could not load the user_chalenge'})
    return JsonResponse({"success": True, 'message': 'Loaded successfully!', 'user_challenge': model_to_dict(user_challenge)})  

@login_required
def update_user_chalenge(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        challenge_id = data.get('challenge_id', 0)
        progress = data.get('progress', 0)

        # Validate
        if not challenge_id or not progress:
                return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
        # Update Progress
        rslt = edit_user_chalenge(request.user, challenge_id, progress)
        if(not rslt.get("success")):
            return JsonResponse({"success": False, 'message': 'Could not Update'}, status=400)
        
        return JsonResponse({"success": True,'message': 'Updated Successfully', 'progress': progress})
    
    return JsonResponse({"success": False, 'message': 'Invalid request method or type.'}, status=400)

## Badge
def list_user_badges(request):
    user_badges = UserBadge.objects.filter(user=request.user).select_related('user', 'badge')
    user_badges_data = [
        {
            "badge": {
                "id": user_badge.badge.id,
                "name": user_badge.badge.name,
                "description": user_badge.badge.description,
            },
            "user": {
                "id": user_badge.user.id,
                "username": user_badge.user.username,
                "email": user_badge.user.email,
            },
            "date": user_badge.date,
        }
        for user_badge in user_badges
    ]
    
    return JsonResponse({"success": True, 'message': 'Badges retrieved successfully!', 'user_badges': user_badges_data})

## Goal
def get_goal(request):
    goal = get_object_or_none(Goal, user=request.user)
    if not goal:
        return JsonResponse({"success": True, 'message': 'Goal retrieved successfully!', 'goal': {}})
    return JsonResponse({"success": True, 'message': 'Goal retrieved successfully!', 'goal': model_to_dict(goal)})

def add_goal(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        goal = data.get('goal', None)
        # Validate
        if not goal or not goal.get('calories', 0):
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    
        goal_check = get_object_or_none(Goal, user=request.user)
        if goal_check:
            return JsonResponse({"success": True, 'message': 'Goal Added successfully!', 'goal': model_to_dict(goal_check)})
        
        try:
            goal = Goal.objects.create(
                user = request.user,
                calories = goal.get('calories'),
                progress = 0
            )
        except Exception as e:
            return JsonResponse({"success": False, 'message': 'Could not save the Goal'}, status=400)
    
        return JsonResponse({"success": True, 'message': 'Goal Added successfully!', 'goal': model_to_dict(goal)})
    
    return JsonResponse({"success": False, 'message': 'Invalid Request Type'}, status=400)

def update_goal(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        goal = data.get('goal', None)
        # Validate
        if not goal or not goal.get('calories', 0):
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
    
        goal_rslt = update_goal_calories(request.user, goal.get('calories'))
        if(not goal_rslt.get('success')):
            return JsonResponse({"success": False, 'message': goal_rslt.get("message", "error")}, status=400)
    
        return JsonResponse({"success": True, 'message': 'Goal Updated successfully!', 'goal': model_to_dict(goal_rslt.get("data"))})
    
    return JsonResponse({"success": False, 'message': 'Invalid Request Type'}, status=400)


## User
@login_required
@transaction.atomic
def summary(request):
    # Activity Summary
    activity_summary_rslt = get_activity_summary(request.user)
    if(not activity_summary_rslt.get('success')):
        return JsonResponse({"success": False, 'message': activity_summary_rslt.get('message', 'An error occurred while fetching data.')}, status=400)
    
    activity_summary = activity_summary_rslt.get('data') or {"points_per_day": [], "total_points": 0, "count": 0}

    # Chalenge Summary
    challenge_summary_rslt = get_challenge_summary(request.user)
    if(not challenge_summary_rslt.get('success')):
        return JsonResponse({"success": False, 'message': challenge_summary_rslt.get('message', 'An error occurred while fetching data.')}, status=400)
       
    challenge_summary = challenge_summary_rslt.get('data') or {"points_per_day": [], "total_points": 0, "count": 0}

    return JsonResponse({"success": True, 'activity_summary': activity_summary, 'challenge_summary': challenge_summary})

## Leaderboard
@login_required
def leaderboard(request):
    leaderboard_rslt = get_top_users_summary()
    if(not leaderboard_rslt.get('success')):
        return JsonResponse({"success": False, 'message': leaderboard_rslt.get('message', 'An error occurred while fetching data.')}, status=400)

    return JsonResponse({"success": True, 'leaderboard': leaderboard_rslt.get('data') or []})
