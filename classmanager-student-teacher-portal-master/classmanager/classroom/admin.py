from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SubmitAssignment, User,Student,StudentMarks,Teacher,StudentsInClass
# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(StudentMarks)
admin.site.register(Teacher)
admin.site.register(StudentsInClass)
admin.site.register(SubmitAssignment)
