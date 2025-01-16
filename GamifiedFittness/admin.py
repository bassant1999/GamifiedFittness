from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Unit)
admin.site.register(Activity)
admin.site.register(UserActivity)
admin.site.register(Challenge)
admin.site.register(UserChallenge)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Goal)



