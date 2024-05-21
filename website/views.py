from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from website.models import Employee, Teams, EvaluationFormModel, AdminFeautures
from .forms import EvaluationForm, FileUploadForm
from django.shortcuts import get_object_or_404
import csv
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
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
    return redirect("home")


@login_required
def evaluation_view(request):
    employee_id = request.GET.get("employee_id")
    form_submitted = False
    disable_form = False
    is_editing = False
    form_enabling_date = AdminFeautures.objects.first()

    print("Received employee_id:", employee_id)  

    if request.method == "POST" and employee_id:
        employee = get_object_or_404(Employee, employee_id=employee_id)

        evaluation_instances = EvaluationFormModel.objects.filter(
            employee=employee
        ).order_by("-id")
        form_instance = evaluation_instances.first()

        print("Form instance:", form_instance) 

        if (
            form_instance
            and form_instance.evaluation_date.month != datetime.today().month
        ):
            form_instance = None

        print("Updated Form instance:", form_instance)  

        form = EvaluationForm(request.POST, instance=form_instance)
        print("Form data:", request.POST)  
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.evaluated_by = request.user
            evaluation.save()
            messages.success(request, "Form submitted successfully!")
            form_submitted = True
            is_editing = True
        else:
            if datetime.now().day >= form_enabling_date.form_enabling_date:
                form_submitted = False
            else:
                messages.error(request, "Please fill the form with relevant data.")

        print("Form errors:", form.errors)  
    else:
        messages.error(request, "Invalid request. Please provide an employee ID.")
        form = EvaluationForm()

    if datetime.now().day >= form_enabling_date.form_enabling_date:
        disable_form = True

    today = datetime.now().date()
    if employee_id:
        employee = get_object_or_404(Employee, employee_id=employee_id)

        print("Employee:", employee)  # Debugging statement

        hb_exp_months = (today.year - employee.joining_date.year) * 12 + (
            today.month - employee.joining_date.month
        )
        hb_exp_years = hb_exp_months // 12
        hb_exp_remaining_months = hb_exp_months % 12
        decimal_months = hb_exp_remaining_months / 12
        experience = hb_exp_years + decimal_months
        hb_exp = f"{experience:.1f} years"
    else:
        hb_exp = None
    
    today = date.today()
    previous_month_date = today - timedelta(days=today.day)
    previous_month = previous_month_date.strftime("%B") 
    previous_year = previous_month_date.strftime("%Y")  
    evaluation_for = f"{previous_month} {previous_year}"

    print("Rendering with data:")  # Debugging statement
    print({
        "form": form,
        "employee": employee if employee_id else None,
        "hb_exp": hb_exp,
        "form_submitted": form_submitted,
        "disable_form": disable_form,
        "is_editing": is_editing,
        "evaluation_for": evaluation_for,
    })

    return render(
        request,
        "evaluation_form.html",
        {
            "form": form,
            "employee": employee if employee_id else None,
            "hb_exp": hb_exp,
            "form_submitted": form_submitted,
            "disable_form": disable_form,
            "is_editing": is_editing,
            "evaluation_for": evaluation_for,
        },
    )




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
