from django.urls import path
from . import views

urlpatterns = [
    ## DashBoard
    path("", views.index, name="index"),
    ## Register, Login, and Log out
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    ## Activity
    path("activities", views.list_activity_view, name="list_activity_view"),
    path("list_activity", views.list_activity, name="list_activity"),
    path("list_user_activity", views.list_user_activity, name="list_user_activity"),
    path("activities/add", views.add_activity, name="add_activity"),
    ## Chalenge
    path("chalenges", views.list_chalenge_view, name="list_chalenge_view"),
    path("chalenges/<int:challenge_id>", views.challenge_view, name="challenge_view"),
    path("chalenges/add", views.add_chalenge, name="add_chalenge"),
    path("chalenges/join/<int:challenge_id>", views.join_chalenge, name="join_chalenge"),
    path("chalenges/leave/<int:challenge_id>", views.leave_chalenge, name="leave_chalenge"),
    path("chalenges/update", views.update_user_chalenge, name="update_user_chalenge"),
    path("chalenges/load_chalenge/<int:challenge_id>", views.load_chalenge, name="load_chalenge"),
    path("list_chalenges", views.list_chalenges, name="list_chalenges"),
    path("user_chalenges", views.list_user_chalenges, name="list_user_chalenges"),
    path("user_chalenges/load_user_chalenge/<int:challenge_id>", views.load_user_chalenge, name="load_user_chalenge"),
    ## Badge
    path("list_user_badges", views.list_user_badges, name="list_user_badges"),
    ## Goal
    path("add_goal", views.add_goal, name="add_goal"),
    path("update_goal", views.update_goal, name="update_goal"),
    path("get_goal", views.get_goal, name="get_goal"),
    ## User
    path("summary", views.summary, name="summary"),
    ## leaderboard
    path("leaderboard", views.leaderboard_view, name="leaderboard_view"),
    path("load_leaderboard", views.leaderboard, name="leaderboard"),
    ## statistics
    path("statistics", views.statistics_view, name="statistics_view"),


]