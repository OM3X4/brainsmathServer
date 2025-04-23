from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from .serializers import UserDataSerializer , TestSerializer , SettingsSerializer , LeaderboardEntitySerializer , registerSerializer
from django.contrib.auth.models import User
from rest_framework import status
from .models import Settings , Test
from rest_framework.permissions import IsAuthenticated
import math


# Create your views here.
@api_view(["GET" , "PUT"])
@permission_classes([IsAuthenticated])
def getUserData(request):
    user =  request.user
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

    page = int(request.GET.get("page" , 0))

    limit = 50
    offset = (page - 1) * limit


    tests = Test.objects.filter(
        mode="time", time=60000
    ).order_by("user", "-qpm").distinct("user")

    testsCount = Test.objects.filter(
        mode="time", time=60000
    ).order_by("user", "-qpm").distinct("user").count()

    sorted_tests = sorted(tests, key=lambda x: x.qpm, reverse=True)[offset:offset + limit]

    serial = LeaderboardEntitySerializer(sorted_tests, many=True)

    return Response({
        "results": serial.data,
        "total_pages": math.ceil(testsCount / 50),
    }, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submitTest(request):
    # TODO: replace this with `request.user` when you add authentication

    user = request.user
    serializer = TestSerializer(data=request.data , partial=True)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def register(request):
    serial = registerSerializer(data=request.data)
    if serial.is_valid():
        user = serial.save()
        Settings.objects.create(theme="discord" , font="ubuntu" , user=user)
        return Response(serial.data , status=status.HTTP_201_CREATED)
    return Response(serial.errors , status=status.HTTP_400_BAD_REQUEST)