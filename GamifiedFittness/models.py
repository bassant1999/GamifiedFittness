from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

class User(AbstractUser):
    pass

# Unit Model
class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)  # minutes, repitations,...

    def __str__(self):
        return self.name

# Activity Model
class Activity(models.Model):
    name = models.CharField(max_length=100) # Running, Push-ups,..
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT)
    points = models.FloatField() # points awarded per unit
    calories = models.FloatField() # Calories burned per unit

    def __str__(self):
        return f'{self.name} - {self.unit.name}'

# User Activity Model
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    activity = models.ForeignKey(Activity, on_delete=models.RESTRICT)
    effort = models.PositiveIntegerField() # value scored in mins, meter,..etc
    points = models.FloatField(blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)
    start_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.calories:
            self.calories = self.activity.calories * self.effort
        if not self.points:
            self.points = self.activity.points * self.effort
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.activity.name} on {self.start_date}'

# Challenge Model
class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.FloatField()
    calories = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    slug = models.SlugField(unique=True, blank=True)
    participants = models.ManyToManyField(User, through="UserChallenge")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_share_link(self):
        return f"{self.get_absolute_url()}"

# User Challenge Model
class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    challenge = models.ForeignKey(Challenge, on_delete=models.RESTRICT)
    progress = models.FloatField(default=0.0)  # percentage
    points_earned = models.FloatField(default=0.0)

    def update_progress(self, new_progress):
        self.progress = new_progress
        self.points_earned = (self.progress / 100) * self.challenge.points
        self.save()

# User Challenge Model
class UserChallengeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    challenge = models.ForeignKey(Challenge, on_delete=models.RESTRICT)
    comment = models.CharField(max_length=500) 
    date = models.DateField()

class UserChallengeReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    ChallengeComment = models.ForeignKey(UserChallengeComment, on_delete=models.RESTRICT)
    reply = models.CharField(max_length=500) 
    date = models.DateField()

# Badge Model
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.TextField()

    def __str__(self):
        return self.name

# User Badge Model
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    badge = models.ForeignKey(Badge, on_delete=models.RESTRICT)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'badge')  # Ensures user-badge combination is unique

    def __str__(self):
        return f'{self.user.username} - {self.badge.name}'

# Goal Model
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    calories = models.FloatField()
    progress = models.FloatField(default=0.0)  # percentage


# Leaderboard View
class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(blank=True, null=True)

    def update_points(self, new_points):
        self.total_points += new_points
        self.save()

