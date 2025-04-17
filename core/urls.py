from django.urls import path
from .views import getUserData , getUserSettings


urlpatterns = [
    path("user/" , getUserData),
]
