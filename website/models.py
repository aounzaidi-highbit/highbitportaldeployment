from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from datetime import date, datetime, timedelta


class Teams(models.Model):
    team_name = models.CharField(max_length=255)

    def __str__(self):
        return self.team_name

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"


class Employee(models.Model):
    username = models.CharField(max_length=40, blank=True)
    password = models.CharField(max_length=40, blank=True)
    employee_id = models.CharField(primary_key=True, max_length=20, default="HB-")
    employee_name = models.CharField(max_length=255)
    employee_email = models.EmailField()
    previous_experience = models.CharField(max_length=255, blank=True)
    joining_date = models.DateField(null=True, editable=True)
    team = models.ForeignKey(
        Teams, on_delete=models.CASCADE, related_name="members", blank=True, null=True
    )
    team_lead = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="team_employees",
        blank=True,
        null=True,
    )

    role = models.CharField(max_length=255)
    is_team_lead = models.BooleanField(default=False)

    def __str__(self):
        return self.employee_name

    def save(self, *args, **kwargs):
        if self.is_team_lead:
            user, created = User.objects.get_or_create(
                username=self.employee_email, defaults={"email": self.employee_email}
            )
            if not created:
                user.set_password(self.password)
                user.save()

        if self.joining_date:
            today = datetime.now().date()
            months_of_experience = (today.year - self.joining_date.year) * 12 + (
                today.month - self.joining_date.month
            )
            self.highbit_experience = f"{months_of_experience} months"

        super(Employee, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_team_lead:
            user_to_delete = User.objects.filter(username=self.employee_email).first()
            if user_to_delete:
                user_to_delete.delete()
        super(Employee, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class EvaluationFormModel(models.Model):
    tl_marks = models.FloatField()
    hr_marks = models.FloatField(
        null=True,
    )
    feedback = models.TextField()
    evaluation_date = models.DateField(default=date.today, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    _weighted_average = models.FloatField(null=True, blank=True)
    evaluation_for = models.CharField(max_length=30, null=True)
    time_stamp = models.TimeField(auto_now=True)
    previous_month = models.CharField(max_length=20, editable=False, blank=True)
    previous_year = models.CharField(max_length=4, editable=False, blank=True)

    class Meta:
        verbose_name = "Evaluation Form"
        verbose_name_plural = "Evaluation Forms"

    def __str__(self):
        return f"Evaluation form submitted by {self.evaluated_by} for {self.employee.employee_name} {self.employee.employee_id}."

    def calculate_weighted_average(self):
        tl_weight = 0.85
        hr_weight = 0.15
        return (self.tl_marks * tl_weight) + (self.hr_marks * hr_weight)

    def save(self, *args, **kwargs):
        today = date.today()
        previous_month_date = today - timedelta(days=today.day)
        self.previous_month = previous_month_date.strftime("%B") 
        self.previous_year = previous_month_date.strftime("%Y")  
        self.evaluation_for = f"{self.previous_month} {self.previous_year}"
        super().save(*args, **kwargs)


@receiver(post_save, sender=EvaluationFormModel)
def calculate_weighted_average(sender, instance, created, **kwargs):
    if not created:
        tl_weight = 0.85
        hr_weight = 0.15
        old_weighted_avg = (
            instance._weighted_average
            if instance._weighted_average is not None
            else 0.0
        )

        if instance.tl_marks is not None:
            new_tl_marks = float(instance.tl_marks) * 10 / 10
        else:
            new_tl_marks = 0.0
        if instance.hr_marks is not None:
            new_hr_marks = float(instance.hr_marks) * 10 / 10
        else:
            new_hr_marks = 0.0
        new_weighted_avg = (new_tl_marks * tl_weight) + (new_hr_marks * hr_weight)

        if new_weighted_avg != old_weighted_avg:
            instance._weighted_average = new_weighted_avg
            instance.save(update_fields=["_weighted_average"])


class AdminFeautures(models.Model):
    form_enabling_date = models.IntegerField()

    def __str__(self):
        return "Form Disabling Date"
