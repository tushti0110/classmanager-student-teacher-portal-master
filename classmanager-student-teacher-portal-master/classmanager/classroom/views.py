from tokenize import String
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView, View)

from classroom import models
from media.checker.visionapi_demo import *
from media.checker.jaccardsimi import *
from media.checker.langcheck import *
from media.checker.keywordextract import *
from media.checker.bert import *
from media.checker.graph2 import *
# Create your views here.
from classroom.forms import (AssignmentForm, MarksForm, MessageForm,
                             NoticeForm, StudentProfileForm,
                             StudentProfileUpdateForm, SubmitForm,
                             TeacherProfileForm, TeacherProfileUpdateForm,
                             UserForm)
from classroom.models import (ClassAssignment, Student, StudentMarks,
                              StudentsInClass, SubmitAssignment, Teacher)


# For Teacher Sign Up
def TeacherSignUp(request):
    user_type = 'teacher'
    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        teacher_profile_form = TeacherProfileForm(data = request.POST)

        if user_form.is_valid() and teacher_profile_form.is_valid():

            user = user_form.save()
            user.is_teacher = True
            user.save()

            profile = teacher_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors,teacher_profile_form.errors)
    else:
        user_form = UserForm()
        teacher_profile_form = TeacherProfileForm()

    return render(request,'classroom/teacher_signup.html',{'user_form':user_form,'teacher_profile_form':teacher_profile_form,'registered':registered,'user_type':user_type})


###  For Student Sign Up
def StudentSignUp(request):
    user_type = 'student'
    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        student_profile_form = StudentProfileForm(data = request.POST)

        if user_form.is_valid() and student_profile_form.is_valid():

            user = user_form.save()
            user.is_student = True
            user.save()

            profile = student_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors,student_profile_form.errors)
    else:
        user_form = UserForm()
        student_profile_form = StudentProfileForm()

    return render(request,'classroom/student_signup.html',{'user_form':user_form,'student_profile_form':student_profile_form,'registered':registered,'user_type':user_type})

## Sign Up page which will ask whether you are teacher or student.
def SignUp(request):
    return render(request,'classroom/signup.html',{})

## login view.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

            else:
                return HttpResponse("Account not active")

        else:
            messages.error(request, "Invalid Details")
            return redirect('classroom:login')
    else:
        return render(request,'classroom/login.html',{})

## logout view.
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

## User Profile of student.
class StudentDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "student"
    model = models.Student
    template_name = 'classroom/student_detail_page.html'

## User Profile for teacher.
class TeacherDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "teacher"
    model = models.Teacher
    template_name = 'classroom/teacher_detail_page.html'

## Profile update for students.
@login_required
def StudentUpdateView(request,pk):
    profile_updated = False
    student = get_object_or_404(models.Student,pk=pk)
    if request.method == "POST":
        form = StudentProfileUpdateForm(request.POST,instance=student)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'student_profile_pic' in request.FILES:
                profile.student_profile_pic = request.FILES['student_profile_pic']
            profile.save()
            profile_updated = True
    else:
        form = StudentProfileUpdateForm(request.POST or None,instance=student)
    return render(request,'classroom/student_update_page.html',{'profile_updated':profile_updated,'form':form})

## Profile update for teachers.
@login_required
def TeacherUpdateView(request,pk):
    profile_updated = False
    teacher = get_object_or_404(models.Teacher,pk=pk)
    if request.method == "POST":
        form = TeacherProfileUpdateForm(request.POST,instance=teacher)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'teacher_profile_pic' in request.FILES:
                profile.teacher_profile_pic = request.FILES['teacher_profile_pic']
            profile.save()
            profile_updated = True
    else:
        form = TeacherProfileUpdateForm(request.POST or None,instance=teacher)
    return render(request,'classroom/teacher_update_page.html',{'profile_updated':profile_updated,'form':form})

## List of all students that teacher has added in their class.
def class_students_list(request):
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            qs_one.append(x)
        else:
            pass
    context = {
        "class_students_list": qs_one,
    }
    template = "classroom/class_students_list.html"
    return render(request, template, context)

class ClassStudentsListView(LoginRequiredMixin,DetailView):
    model = models.Teacher
    template_name = "classroom/class_students_list.html"
    context_object_name = "teacher"

## For Marks obtained by the student in all subjects.
class StudentAllMarksList(LoginRequiredMixin,DetailView):
    model = models.Student
    template_name = "classroom/student_allmarks_list.html"
    context_object_name = "student"

## To give marks to a student.
@login_required
def add_marks(request,pk):
    error = True
    student = get_object_or_404(models.Student,pk=pk)
    teacher = request.user.Teacher
       
    folder_path = r'C:\Users\tusht\Downloads\classmanager-student-teacher-portal-master\classmanager-student-teacher-portal-master\classmanager\media\assignments'
    image_path = 'writesample.png'
    list1 = api(folder_path, image_path)
    list2 = "the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a by-product."
    
    given_marks = 0
    score_jaccard = round(2 * jaccard(list1,list2),2)
    score_language_check = round(2 * language_Check(list2),2)
    score_keyword_matching = round(2 * keywordextract(list1, list2),2)
    score_bert = round(2 * callbert(list1),2)
    score_graph = graph(list1,list2)
    
    given_marks = round(score_jaccard + score_language_check + score_keyword_matching + score_bert + score_graph,2)
    return render(request,'classroom/add_marks.html',{'student':student,'given_marks':given_marks, 'score_jaccard':score_jaccard,'score_language_check': score_language_check,'score_keyword_matching':score_keyword_matching, 'score_bert':score_bert, 'score_graph': score_graph})

## For updating marks.
@login_required
def update_marks(request,pk):
    marks_updated = False
    obj = get_object_or_404(StudentMarks,pk=pk)
    if request.method == "POST":
        form = MarksForm(request.POST,instance=obj)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.save()
            marks_updated = True
    else:
        form = MarksForm(request.POST or None,instance=obj)
    return render(request,'classroom/update_marks.html',{'form':form,'marks_updated':marks_updated})


## To see the list of all the marks given by the techer to a specific student.
@login_required
def student_marks_list(request,pk):
    error = True
    student = get_object_or_404(models.Student,pk=pk)
    teacher = request.user.Teacher

    given_marks = 0
    folder_path = r'C:\Users\tusht\Downloads\classmanager-student-teacher-portal-master\classmanager-student-teacher-portal-master\classmanager\media\assignments'
    image_path = 'writesample.png'
    list1 = api(folder_path, image_path)
    list2 = "the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a by-product."
    
    score_jaccard = round(2 * jaccard(list1,list2),2)
    score_language_check = round(2 * language_Check(list2),2)
    score_keyword_matching = round(2 * keywordextract(list1, list2),2)
    score_bert = round(2 * callbert(list1),2)
    score_graph = round(2 * graph(list1,list2))
    
    given_marks = round(score_jaccard + score_language_check + score_keyword_matching + score_bert + score_graph,2)
    return render(request,'classroom/student_marks_list.html',{'student':student,'given_marks':given_marks, 'score_jaccard':score_jaccard,'score_language_check': score_language_check,'score_keyword_matching':score_keyword_matching, 'score_bert':score_bert, 'score_graph': score_graph})

## To add student in the class.
class add_student(LoginRequiredMixin,generic.RedirectView):

    def get_redirect_url(self,*args,**kwargs):
        return reverse('classroom:students_list')

    def get(self,request,*args,**kwargs):
        student = get_object_or_404(models.Student,pk=self.kwargs.get('pk'))

        try:
            StudentsInClass.objects.create(teacher=self.request.user.Teacher,student=student)
        except:
            messages.warning(self.request,'warning, Student already in class!')
        else:
            messages.success(self.request,'{} successfully added!'.format(student.name))

        return super().get(request,*args,**kwargs)

@login_required
def student_added(request):
    return render(request,'classroom/student_added.html',{})

## List of students which are not added by teacher in their class.
def students_list(request):
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            pass
        else:
            qs_one.append(x)

    context = {
        "students_list": qs_one,
    }
    template = "classroom/students_list.html"
    return render(request, template, context)

## List of all the teacher present in the portal.
def teachers_list(request):
    query = request.GET.get("q", None)
    qs = Teacher.objects.all()
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )

    context = {
        "teachers_list": qs,
    }
    template = "classroom/teachers_list.html"
    return render(request, template, context)

## Teacher uploading assignment.
@login_required
def upload_assignment(request):
    assignment_uploaded = False
    teacher = request.user.Teacher
    students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
            upload.save()
            upload.student.add(*students)
            assignment_uploaded = True
    else:
        form = AssignmentForm()
    return render(request,'classroom/upload_assignment.html',{'form':form,'assignment_uploaded':assignment_uploaded})

## Students getting the list of all the assignments uploaded by their teacher.
@login_required
def class_assignment(request):
    student = request.user.Student
    assignment = SubmitAssignment.objects.filter(student=student)
    assignment_list = [x.submitted_assignment for x in assignment]
    return render(request,'classroom/class_assignment.html',{'student':student,'assignment_list':assignment_list})

## List of all the assignments uploaded by the teacher himself.
@login_required
def assignment_list(request):
    teacher = request.user.Teacher
    context = api()
    return render(request,'classroom/assignment_list.html',{'teacher':teacher, 'context':context})

## For updating the assignments later.
@login_required
def update_assignment(request,id=None):
    obj = get_object_or_404(ClassAssignment, id=id)
    form = AssignmentForm(request.POST or None, instance=obj)
    context = {
        "form": form
    }
    if form.is_valid():
        obj = form.save(commit=False)
        if 'assignment' in request.FILES:
            obj.assignment = request.FILES['assignment']
        obj.save()
        messages.success(request, "Updated Assignment".format(obj.assignment_name))
        return redirect('classroom:assignment_list')
    template = "classroom/update_assignment.html"
    return render(request, template, context)

## For deleting the assignment.
@login_required
def assignment_delete(request, id=None):
    obj = get_object_or_404(ClassAssignment, id=id)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Assignment Removed")
        return redirect('classroom:assignment_list')
    context = {
        "object": obj,
    }
    template = "classroom/assignment_delete.html"
    return render(request, template, context)

## For students submitting their assignment.
@login_required
def submit_assignment(request, id=1):
    student = request.user.Student
    assignment = get_object_or_404(ClassAssignment, id=id)
    teacher = assignment.teacher
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            upload.student = student
            upload.submitted_assignment = assignment
            upload.save()
            return redirect('classroom:class_assignment')
    else:
        form = SubmitForm()
    return render(request,'classroom/submit_assignment.html',{'form':form,})

## To see all the submissions done by the students.
@login_required
def submit_list(request):
    teacher = request.user.Teacher
    return render(request,'classroom/submit_list.html',{'teacher':teacher})

##################################################################################################

## For changing password.
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST , user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed")
            return redirect('home')
        else:
            return redirect('classroom:change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form':form}
        return render(request,'classroom/change_password.html',args)

