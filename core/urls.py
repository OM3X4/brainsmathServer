from django.urls import path
from .views import getUserData , getLeaderboard , hi , submitTest


urlpatterns = [
    path("user/" , getUserData),
    path("leaderboard/" , getLeaderboard),
    path("hi/" , hi),
    path("test/" , submitTest)

]
