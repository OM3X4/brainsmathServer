from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from .serializers import UserDataSerializer , TestSerializer , SettingsSerializer , LeaderboardEntitySerializer , registerSerializer
from django.contrib.auth.models import User
from rest_framework import status
from .models import Settings , Test
from rest_framework.permissions import IsAuthenticated
import math
from django.db import connection


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
    page = int(request.GET.get("page", 1))  # Default to page 1 instead of 0
    limit = 50
    offset = (page - 1) * limit

    query = """
        SELECT
            t.id,
            t.qpm,
            t.raw,
            t.accuracy,
            t.mode,
            t.difficulty,
            t.creation,
            t.number,
            t.time,
            t.user_id,
            u.username
        FROM core_test t
        JOIN auth_user u ON t.user_id = u.id
        WHERE t.qpm = (
            SELECT MAX(qpm)
            FROM core_test
            WHERE user_id = t.user_id
        )
        ORDER BY t.qpm DESC
        LIMIT %s OFFSET %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [limit, offset])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]


    count = len(results)
    return Response({"results": results , "count": count})


@api_view(["GET"])
def getUserRank(request):
    user = request.GET.get("user")

    query = """
        WITH result as (
        SELECT
            t.id,
            t.qpm,
            t.raw,
            t.accuracy,
            t.mode,
            t.difficulty,
            t.creation,
            t.number,
            t.time,
            t.user_id,
            u.username,
            ROW_NUMBER() OVER (ORDER BY t.qpm DESC) AS index
            FROM core_test t
            JOIN auth_user u ON t.user_id = u.id
            WHERE t.qpm = (
                SELECT MAX(qpm)
                FROM core_test
                WHERE user_id = t.user_id
            )
        ORDER BY t.qpm DESC)
        SELECT * FROM result
        WHERE username = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query , [user])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return Response({"result": results})







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