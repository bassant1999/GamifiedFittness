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
from .services.user_activity import *
from .services.user_chalenge import *
from .services.challenge import *
from django.forms.models import model_to_dict
from GamifiedFittness.constants import *


@transaction.atomic
def index(request):
    # Activity Summary
    activity_summary_rslt = get_activity_summary(request.user)
    if(not activity_summary_rslt.get('success')):
        return render(request, "GamifiedFittness/error.html", {
            'error_message': activity_summary_rslt.get('error', 'An error occurred while fetching data.')
        })
    activity_summary = activity_summary_rslt.get('data') or {"points_per_day": [], "total_points": 0, "count": 0}
    # Chalenge Summary
    challenge_summary_rslt = get_challenge_summary(request.user)
    if(not challenge_summary_rslt.get('success')):
        return render(request, "GamifiedFittness/error.html", {
            'error_message': challenge_summary_rslt.get('error', 'An error occurred while fetching data.')
        })
    challenge_summary = challenge_summary_rslt.get('data') or {"points_per_day": [], "total_points": 0, "count": 0}

    #  Badges
    user_badges = UserBadge.objects.filter(user=request.user)

    #  Goal
    goal = get_object_or_none(Goal, user=request.user)
    formatted_goal = {}
    if goal:
            formatted_goal = {
                "progress_precentage": goal.progress * 100,
                "progress": goal.progress,
                "calories": goal.calories
                }
    # # Summary
    # summary = {
    #     "total_points": activity_summary.total_points + challenge_summary.total_points,
    #     "rank": 0,
    #  "calories"
    #     "Goal": 0,
    # }

    print(activity_summary)
    print(challenge_summary)


    return render(request, "GamifiedFittness/dashboard.html", 
                  {
                      "summary": {
                            'activity_summary': activity_summary,
                            'challenge_summary': challenge_summary,
                            "total_points": activity_summary.get('total_points') + challenge_summary.get('total_points'),
                            "total_calories": activity_summary.get('total_calories') + challenge_summary.get('total_calories')
                      },
                      'user_badges': user_badges,
                      "goal": formatted_goal
                  })

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
        return HttpResponseRedirect(reverse("index"))
    
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
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "GamifiedFittness/register.html")


def product_list_view(request):
    # Get all products from the database
    products = User.objects.all()
    
    # Serialize the queryset to JSON
    product_data = serializers.serialize('json', products)
    
    # Return JSON response
    return JsonResponse({'products': product_data}, safe=False)



# Activity
@login_required
def list_activity(request):
   # Filter
    filter = {
        'name': request.GET.get('filter[name]', ''),
        'date': request.GET.get('filter[date]', ''),
    }
    
    filter_conditions = Q(user=request.user)
    if filter['name']:
        filter_conditions &= Q(activity__name__icontains=filter['name'])

    if filter['date']:
        filter_conditions &= Q(start_date=filter['date'])

    # Activities
    User_activities = UserActivity.objects.filter(filter_conditions).order_by('-start_date')

    activities = Activity.objects.filter()
    # activity_types = [e.value for e in ActivityType]

    return render(request, 'GamifiedFittness/activity_list.html', {'User_activities': User_activities, 'filter': filter, "activities": activities})



def view_activity(request, id):
    # Fetch the activity by id or return a 404 error if not found
    activity = get_object_or_404(Activity, pk=id)
    return render(request, 'GamifiedFittness/activity_view.html', {'activity': activity})


@login_required
@transaction.atomic
def add_activity(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        activity_id = request.POST.get('activity')
        effort = request.POST.get('effort')
        start_date = request.POST.get('start_date')

        if not activity_id or not effort or not start_date:
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)

        rslt = create_activity(request.user, activity_id, effort, start_date)
        if not rslt:
            return JsonResponse({"success": False, 'message': 'Could not save the activity'}, status=400)
        
        return JsonResponse({"success": True, 'message': 'Activity added successfully!', 'user_activity': model_to_dict(rslt.get('data'))})

    return JsonResponse({'error': 'Invalid request method or type.'}, status=400)


@login_required
def list_chalenge(request):
    # Chalenges
    chalenges_list = Challenge.objects.all().order_by('-start_date')
    paginator = Paginator(chalenges_list, 10)
    page = request.GET.get('page')
    try:
        chalenges = paginator.page(page)
    except PageNotAnInteger:
        chalenges = paginator.page(1)
    except EmptyPage:
        chalenges = paginator.page(paginator.num_pages)

    return render(request, 'GamifiedFittness/chalenge_list.html', {'chalenges': chalenges})

@login_required
def add_chalenge(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        description = request.POST.get('description', None)
        points = request.POST.get('points')
        calories = request.POST.get('calories')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Validate
        if not name or not points or not calories or not start_date or not end_date:
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
        
        # Add Challenge
        challenge_rslt = add_challenge(request.user, name, points, calories, start_date, end_date, description)
        if(not challenge_rslt.get('success')):
                return JsonResponse({'error': 'Could not add the challenge.'}, status=400)

        challenge = challenge_rslt.get('data')

        return JsonResponse({"success": True, 'message': 'Challenge added successfully!'})
    
    return JsonResponse({'error': 'Invalid request method or type.'}, status=400)

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
        return JsonResponse({"success": True, 'message': 'Joined successfully!', 'user_challenge': model_to_dict(user_challenge)})    
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
   
    return JsonResponse({"success": True, 'message': 'Joined successfully!', 'user_challenge': model_to_dict(user_challenge)})    

@login_required
def view_chalenge(request, challenge_id):
    share_link = request.build_absolute_uri(f"/challenges/{challenge_id}/join")
    print(share_link)

@login_required
def update_user_chalenge(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        challenge_id = data.get('challenge_id', -1)
        progress = data.get('progress', 0)

        rslt = edit_user_chalenge(request.user, challenge_id, int(progress))
        print(rslt)
        if(not rslt.get("success")):
            return JsonResponse({"success": False, 'message': 'Could not Update'}, status=400)
        return JsonResponse({'status': 'success', 'progress': progress})

@login_required
def share_chalenge(request, challenge_id):
    share_link = request.build_absolute_uri(f"/chalenges/{challenge_id}")
    print(share_link)





# @csrf_exempt
# def list_activities(request):
#     activities = Activity.objects.all()
#     return JsonResponse({'result': True, 'object': [{"name": "test", "id": 1}]})
    
# @csrf_exempt
# def add_activity(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         obj_activity = data.get('objActivity', {})
#         if 'name' in obj_activity and 'unit' in obj_activity:
#             activity = Activity(name=obj_activity['name'], unit=obj_activity['unit'])
#             activity.save()
#             return JsonResponse({'result': True, 'title': 'Success', 'message': 'Activity added successfully.'})
#         return JsonResponse({'result': False, 'title': 'Error', 'message': 'Invalid data.'})
#     return JsonResponse({'result': False, 'title': 'Error', 'message': 'Invalid request method.'})