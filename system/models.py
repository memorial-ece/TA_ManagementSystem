from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class TA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cv = models.FileField()
    availableHours = models.FloatField(default=0)


class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Course(models.Model):
    instructor = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    CRN = models.CharField(max_length=5)
    semester = models.CharField(max_length=10)
    title = models.CharField(max_length=50)
    subject = models.CharField(max_length=4)
    courseName = models.CharField(max_length=30)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.subject + self.courseName


class TADuty(models.Model):
    curriculum = models.ForeignKey(Course, on_delete=models.CASCADE)
    labNumber = models.IntegerField(default=0)
    preparationHour = models.FloatField(default=0)
    labHour = models.FloatField(default=0)
    labWorkingHour = models.FloatField(default=0)
    assignmentNumber = models.IntegerField(default=0)
    assignmentWorkingHour = models.FloatField(default=0)
    contactHour = models.FloatField(default=0)
    otherDutiesHour = models.FloatField(default=0)
    totalHour = models.FloatField(default=0)

    def __str__(self):
        return self.curriculum.subject + self.curriculum.courseName



