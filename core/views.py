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
        # columns = [col[0] for col in cursor.description]
        # results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        results = cursor.fetchall()

    count = len(results)
    return Response({"results": results , "count": count})

# @api_view(["GET"])
# def getLeaderboard(request):
#     page = int(request.GET.get("page", 1))  # Default to page 1 instead of 0
#     limit = 50
#     offset = (page - 1) * limit

#     # Use a subquery to get the highest qpm test for each user
#     from django.db.models import OuterRef, Subquery, Max, F

#     # Find the max qpm per user
#     user_max_tests = Test.objects.filter(
#         mode="time",
#         time=60000,
#         user=OuterRef('user')
#     ).order_by('-qpm').values('id')[:1]

#     # Get the actual test records with those max qpm values
#     tests = Test.objects.filter(
#         id__in=Subquery(user_max_tests),
#         mode="time",
#         time=60000
#     ).order_by('-qpm')

#     # Count total unique users with qualifying tests
#     total_count = tests.count()

#     # Add rank directly in the database query when possible
#     # For PostgreSQL you can use window functions:
#     from django.db.models.expressions import Window
#     from django.db.models.functions import Rank

#     if connection.vendor == 'postgresql':
#         tests = tests.annotate(
#             rank=Window(
#                 expression=Rank(),
#                 order_by=F('qpm').desc()
#             )
#         )

#     # Paginate results
#     paginated_tests = tests[offset:offset + limit]

#     # Add ranks manually only if not using PostgreSQL
#     if connection.vendor != 'postgresql':
#         for idx, test in enumerate(paginated_tests):
#             test.rank = offset + idx + 1

#     serial = LeaderboardEntitySerializer(paginated_tests, many=True)

    return Response({
        "results": serial.data,
        "total_pages": math.ceil(total_count / limit),
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