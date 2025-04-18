from django.urls import path
from .views import getUserData , getLeaderboard


urlpatterns = [
    path("user/" , getUserData),
    path("leaderboard/" , getLeaderboard),

]
