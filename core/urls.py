from django.urls import path
from .views import getUserData , getLeaderboard , hi , submitTest , register , getUserRank


urlpatterns = [
    path("user/" , getUserData),
    path("leaderboard/" , getLeaderboard),
    path("hi/" , hi),
    path("test/" , submitTest),
    path("register/" , register),
    path("userrank/" , getUserRank),

]
