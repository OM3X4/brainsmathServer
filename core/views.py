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
def hi(request):
    return Response("hi" , status=status.HTTP_200_OK)

@api_view(["GET"])
def getUserSettings(request):
    user =  User.objects.first()
    data = Settings.objects.filter(user=user).first()
    serial = SettingsSerializer(data)
    return Response(serial.data , status=status.HTTP_200_OK)

@api_view(["GET"])
def getLeaderboard(request):
    tests = Test.objects.filter(
        mode="time", time=60000
    ).order_by("user", "-qpm").distinct("user")

    sorted_tests = sorted(tests, key=lambda x: x.qpm, reverse=True)

    serial = LeaderboardEntitySerializer(sorted_tests, many=True)
    return Response(serial.data, status=status.HTTP_200_OK)

@api_view(["POST"])
def submitTest(request):
    user = User.objects.first()
    serializer = TestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

