from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # Activity
    path("activities", views.list_activity, name="list_activity"),
    path('activities/<int:id>/', views.view_activity, name='view_activity'),
    path("activities/add", views.add_activity, name="add_activity"),

    # Chalenge
    path("chalenges", views.list_chalenge, name="list_chalenge"),
    path("chalenges/add", views.add_chalenge, name="add_chalenge"),
    path("chalenges/<int:challenge_id>", views.view_chalenge, name="view_chalenge"),
    path("chalenges/join/<int:challenge_id>", views.join_chalenge, name="join_chalenge"),
    path("chalenges/update", views.update_user_chalenge, name="update_user_chalenge"),


    # path('activities/list', views.list_activities, name='list_activities'),

    
    path('product-list/', views.product_list_view, name='product_list'),
]