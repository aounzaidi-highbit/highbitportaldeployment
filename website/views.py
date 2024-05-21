from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from website.models import Employee, Teams
from .forms import EvaluationForm, FileUploadForm
from django.shortcuts import get_object_or_404
import csv
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.contrib.auth.models import User
# Create your views here.

def home(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "There was a log in error")
            return redirect("home")
    else:
        return render(request, "home.html")

@login_required 
def dashboard(request):
    try:
        logged_in_user = request.user
        emp = Employee.objects.get(employee_email=logged_in_user)
        emps = Employee.objects.filter(team_lead=emp).all()
        return render(
            request, "team_lead_dashboard.html", {"team_lead": emp, "employees": emps}
        )
    except:
        return HttpResponse("You are not authenticated to view this page.")

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have beeen logged out")
    return redirect("home")

@login_required
def evaluation_view(request):

    employee_id = request.GET.get("employee_id")
    form_submitted = False

    if request.method == "POST" and employee_id:
        form = EvaluationForm(request.POST)
        if form.is_valid():

            employee = get_object_or_404(Employee, employee_id=employee_id)
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.evaluated_by = request.user
            evaluation.save()
            messages.success(request, "Form submitted successfully!")
            form_submitted = True
        else:
            messages.error(request, "Please fill the form with relevant data.")
    else:   
        messages.error(request, "Invalid request. Please provide an employee ID.")
        form = EvaluationForm()

    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, "evaluation_form.html", {"form": form, "employee": employee, "form_submitted": form_submitted})



def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]
            handle_uploaded_file(csv_file)
            return render(request, "upload_success.html")
    else:
        form = FileUploadForm()
    context = {"form": form}
    return render(request, "upload_form.html", context)


def handle_uploaded_file(csv_file):
    reader = csv.DictReader(csv_file.read().decode("utf-8").splitlines())

    for row in reader:
        team_name = row["team"]
        team_lead_name = row["team_lead"]

        team_instance, _ = Teams.objects.get_or_create(team_name=team_name)

        is_team_lead = row.get("is_team_lead", "").lower() == "true"
        team_lead_instance = None
        if team_lead_name:
            team_lead_instance, _ = Employee.objects.get_or_create(
                employee_name=team_lead_name,
                defaults={"employee_email": "", "role": "", "is_team_lead": True},
            )

        username = row.get("username", "default_username")

        employee, created = Employee.objects.update_or_create(
            employee_id=row["employee_id"],
            defaults={
                "username": username,
                "password": row["password"],
                "employee_name": row["employee_name"],
                "employee_email": row["employee_email"],
                "previous_experience": row["previous_experience"],
                "highbit_experience": row["highbit_experience"],
                "team": team_instance,
                "team_lead": team_lead_instance,
                "role": row["role"],
                "is_team_lead": is_team_lead,
            },
        )







# def evaluation_view(request):
#     employee_id = request.GET.get("employee_id")
#     form_submitted = False
#     disable_form = False
#     employee = None  # Initialize employee variable

#     if request.method == "POST" and employee_id:
#         form = EvaluationForm(request.POST)
#         if form.is_valid():
#             employee = get_object_or_404(Employee, employee_id=employee_id)
#             evaluation_instance = EvaluationFormModel.objects.filter(employee=employee).first()
#             if evaluation_instance:
#                 form = EvaluationForm(request.POST, instance=evaluation_instance)
#             if not disable_form:  # Check if the form should be disabled
#                 evaluation = form.save(commit=False)
#                 evaluation.employee = employee
#                 evaluation.evaluated_by = request.user
#                 evaluation.save()
#                 messages.success(request, "Form submitted successfully!")
#                 form_submitted = True
#         else:
#             messages.error(request, "Please fill the form with relevant data.")
#     else:
#         messages.error(request, "Invalid request. Please provide an employee ID.")
#         form = EvaluationForm()

#     # Check if it's past the 15th of the month
#     if datetime.now().day > 15:  # Corrected day check
#         disable_form = True
#         messages.error(request, "Evaluation Time is up.")

#     # Fetch the evaluation form for the employee if it exists
#     if employee_id:
#         employee = get_object_or_404(Employee, employee_id=employee_id)
#         evaluation_instance = EvaluationFormModel.objects.filter(employee=employee).first()
#         if evaluation_instance:
#             form = EvaluationForm(instance=evaluation_instance)  # Pass the instance to the form

#     return render(request, "evaluation_form.html", {"form": form, "employee": employee, "form_submitted": form_submitted, "disable_form": disable_form})