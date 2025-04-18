from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserDataSerializer , TestSerializer , SettingsSerializer , LeaderboardEntitySerializer
from django.contrib.auth.models import User
from rest_framework import status
from .models import Settings , Test
from django.db.models import Max


# Create your views here.
@api_view(["GET" , "PUT"])
def getUserData(request):
    user =  User.objects.first()
    settings = Settings.objects.filter(user=user).first()

    if request.method == "GET":
        serial = UserDataSerializer(user)
        return Response(serial.data , status=status.HTTP_200_OK)
    else:
        serializer = SettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getUserSettings(request):
    user =  User.objects.first()
    data = Settings.objects.filter(user=user).first()
    serial = SettingsSerializer(data)
    return Response(serial.data , status=status.HTTP_200_OK)

@api_view(["GET"])
def getLeaderboard(request):
    highest_qpm_per_user = (
    Test.objects
        .values("user")  # Group by user
        .annotate(max_qpm=Max("qpm"))  # Get highest qpm for each user
    )

    serial = LeaderboardEntitySerializer(tests , many=True)
    return Response(serial.data , status=status.HTTP_200_OK)

