from rest_framework import serializers
from .models import Test , Settings
from django.contrib.auth.models import User
from collections import defaultdict

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
        fields = ["username" , "date_joined" , "best_scores" , "font" , "theme" , "tests"]

    def get_best_scores(self , obj):
        result = defaultdict(lambda: defaultdict(dict))
        times = [30 , 60 , 120 , 180]
        questions = [5 , 10 , 15 , 25]
        for time in times:
            for i in range(5):
                # result["time"][time][i + 1] = Test.objects.filter(user=obj , time=time , difficulty=i + 1).first()
                test = Test.objects.order_by("-qpm").filter(user=obj , time=time , difficulty=i + 1).first()
                result["time"][time][i + 1] = TestSerializer(test).data if test else None
        for question in questions:
            for i in range(5):
                # result["questions"][question][i + 1] = Test.objects.filter(user=obj , number=question , difficulty=i + 1).first()
                test = Test.objects.order_by("-qpm").filter(user=obj , number=question , difficulty=i + 1).first()
                result["questions"][question][i + 1] = TestSerializer(test).data if test else None
        return result

    def get_theme(self , obj):
        data = Settings.objects.filter(user=obj).first()
        return data.theme

    def get_font(self , obj):
        data = Settings.objects.filter(user=obj).first()
        return data.font

    def get_tests(self , obj):
        return TestSerializer(Test.objects.filter(user=obj).all() , many=True).data

class LeaderboardEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["qpm" , "raw" , "accuracy" , "creation" , "user" , "number" , "mode"]