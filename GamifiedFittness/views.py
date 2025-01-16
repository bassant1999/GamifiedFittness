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
from django.forms.models import model_to_dict


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

    # # Summary
    # summary = {
    #     "total_points": activity_summary.total_points + challenge_summary.total_points,
    #     "rank": 0,
    #  "calories"
    #     "Goal": 0,
    #     "Badges":0
    # }

    return render(request, "GamifiedFittness/dashboard.html", 
                  {
                      'activity_summary': activity_summary,
                      'challenge_summary': challenge_summary
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
    return HttpResponseRedirect(reverse("index"))


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
    Filter = {
        'name': request.GET.get('filter[name]', ''),
        'date': request.GET.get('filter[date]', ''),
    }
    
    filter_conditions = Q(user=request.user)
    if Filter['name']:
        filter_conditions &= Q(activity__name__icontains=Filter['name'])

    if Filter['date']:
        filter_conditions &= Q(start_date=Filter['date'])

    # Activities
    UserActivities = UserActivity.objects.filter(filter_conditions)

    return render(request, 'GamifiedFittness/activity_list.html', {'UserActivities': UserActivities, 'Filter': Filter})



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
        
        return JsonResponse({"success": True, 'message': 'Activity added successfully!', 'user_activity': rslt.get('data')})
    
        # # Validate activity existence
        # try:
        #     activity = Activity.objects.get(id=activity_id)
        # except Activity.DoesNotExist:
        #     return JsonResponse({'error': 'Selected activity does not exist.'}, status=400)

        # # Create UserActivity instance
        # user_activity = UserActivity.objects.create(
        #     user=request.user,
        #     activity=activity,
        #     effort=int(effort),
        #     start_date=start_date or now()
        # )

        # # Badge
        # if(UserActivity.objects.filter(user=request.user).count() == 1):
        #     # First Activity Bandge
        #     try:
        #         first_activity_badge = Badge.objects.get(id=1)
        #         first_activity_user_badge = UserBadge(user=request.user, badge=first_activity_badge, date=now())
        #         first_activity_user_badge.save()
        #     except Badge.DoesNotExist:
        #         # Handle the case where the badge with id=1 does not exist
        #         return JsonResponse({'error': 'Badge not found.'}, status=404)
        
        # try:   
        #     running_activity = Activity.objects.get(id=1)
        #     total_effort = UserActivity.objects.filter(activity=running_activity).aggregate(Sum('effort'))['effort__sum'] or 0
        #     if(total_effort >= 100):
        #         try:
        #             hundred_km_run_badge = Badge.objects.get(id=2)
        #             hundred_km_run_user_badge = UserBadge(user=request.user, badge=hundred_km_run_badge, date=now())
        #             hundred_km_run_user_badge.save()
        #         except Badge.DoesNotExist:
        #             # Handle the case where the badge with id=1 does not exist
        #             return JsonResponse({'error': 'Badge not found.'}, status=404)

        # except Activity.DoesNotExist:
        #     # Handle the case where the badge with id=1 does not exist
        #     return JsonResponse({'error': 'Activity not found.'}, status=404)


        # # Goal
        # try:
        #     # get appropiate goal
        #     goal = Goal.objects.get(Q(start_date__lte=start_date) & Q(end_date__gte=start_date))
        #     # Update the progress
        #     updated_progress = goal.progress + (user_activity.calories/ goal.calories)
        #     goal.progress = min(updated_progress, 1.0)
        #     goal.save()
        # except Goal.DoesNotExist:
        #     pass
        # except Goal.MultipleObjectsReturned:
        #      return JsonResponse({'error': 'Selected activity does not exist.'}, status=400)


        # return JsonResponse({'message': 'Activity added successfully!', 'user_activity_id': user_activity.id})

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
        description = request.POST.get('description')
        points = request.POST.get('points')
        calories = request.POST.get('calories')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    

        if not name or not points or not calories or not start_date or not end_date:
            return JsonResponse({"success": False, 'message': 'Missing required parameters'}, status=400)
        # Create Challenge instance
        try:
            challenge = Challenge.objects.create(
                name=name,
                description=description,
                points=points,
                calories=calories,
                start_date=start_date,
                end_date=end_date,
            )
        except Exception as e:
            return JsonResponse({"success": False, 'message': 'Could not save the Challenge'}, status=400)
        
        return JsonResponse({"success": True, 'message': 'Challenge added successfully!', 'challenge': challenge})
    
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