from django.db import models
from django.contrib.auth.models import User

class Test(models.Model):

    mode_choices = (
        ('questions', 'questions'),
        ('time', 'time'),
    )


    qpm = models.FloatField()
    raw = models.FloatField()
    accuracy = models.SmallIntegerField()
    mode = models.CharField(max_length=10 , choices=mode_choices)
    difficulty = models.SmallIntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    number = models.IntegerField()
    time = models.IntegerField() # in ms

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.qpm)

class Settings(models.Model):
    theme = models.CharField(max_length=30)
    font = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.theme)

