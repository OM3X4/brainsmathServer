from rest_framework import serializers
from .models import Test , Settings
from django.contrib.auth.models import User
from collections import defaultdict
import time

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'

class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'

class UserDataSerializer(serializers.ModelSerializer):

    best_scores = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()
    font = serializers.SerializerMethodField()
    tests = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ["username" , "date_joined" , "best_scores" , "theme" , "font" , "tests"]

    def get_best_scores(self, obj):

        result = defaultdict(lambda: defaultdict(dict))
        tests = (
            Test.objects.filter(user=obj)
            .order_by("-qpm")
        )
        time_scores = {}
        question_scores = {}

        for test in tests:
            if test.time and (test.time, test.difficulty) not in time_scores:
                time_scores[(test.time, test.difficulty)] = test
            if test.number and (test.number, test.difficulty) not in question_scores:
                question_scores[(test.number, test.difficulty)] = test

        for time in [30, 60, 120, 180]:
            for i in range(1, 6):
                test = time_scores.get((time, i))
                result["time"][time][i] = TestSerializer(test).data if test else None

        for question in [5, 10, 15, 25]:
            for i in range(1, 6):
                test = question_scores.get((question, i))
                result["questions"][question][i] = TestSerializer(test).data if test else None

        return result

    def get_theme(self , obj):
        data = Settings.objects.filter(user=obj).first()
        return data.theme

    def get_font(self , obj):
        data = Settings.objects.filter(user=obj).first()
        return data.font

    def get_tests(self , obj):
        return TestSerializer(Test.objects.filter(user=obj).all()[:10] , many=True).data

class LeaderboardEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["qpm" , "raw" , "accuracy" , "creation" , "user" , "number" , "mode"]