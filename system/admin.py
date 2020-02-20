from django.contrib import admin
from .models import Teacher, TA, DepartmentHead, Course, TADuty, RankTA

admin.site.register(Teacher)
admin.site.register(TA)
admin.site.register(DepartmentHead)
admin.site.register(Course)
admin.site.register(TADuty)
admin.site.register(RankTA)