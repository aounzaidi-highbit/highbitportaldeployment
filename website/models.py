from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from datetime import date


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
    highbit_experience = models.CharField(max_length=255, blank=True)

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
                username=self.employee_email,
                defaults={'email': self.employee_email}
            )
            if not created:
                user.set_password(self.password)
                user.save()

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


MONTH_CHOICES = (
    ("January", _("January")),
    ("February", _("February")),
    ("March", _("March")),
    ("April", _("April")),
    ("May", _("May")),
    ("June", _("June")),
    ("July", _("July")),
    ("August", _("August")),
    ("September", _("September")),
    ("October", _("October")),
    ("November", _("November")),
    ("December", _("December")),
)


class EvaluationFormModel(models.Model):
    tl_marks = models.FloatField()
    hr_marks = models.FloatField(null=True)
    feedback = models.TextField()
    evaluation_date = models.DateField(default=date.today,editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    evaluated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    _weighted_average = models.FloatField(null=True, blank=True)
    evaluation_for = models.CharField(
        max_length=255, choices=MONTH_CHOICES, default="April"
    )

    def __str__(self):
        return f"Evaluation form submitted by {self.evaluated_by} for {self.employee.employee_name} {self.employee.employee_id}."

    class Meta:
        verbose_name = "Evaluation Form"
        verbose_name_plural = "Evaluation Forms"

    def calculate_weighted_average(self):
        tl_weight = 0.85
        hr_weight = 0.15
        return (self.tl_marks * tl_weight) + (self.hr_marks * hr_weight)


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
        new_tl_marks = instance.tl_marks * 20 / 10
        new_hr_marks = instance.hr_marks * 20 / 10
        new_weighted_avg = (new_tl_marks * tl_weight) + (new_hr_marks * hr_weight)

        if new_weighted_avg != old_weighted_avg:
            instance._weighted_average = new_weighted_avg
            instance.save(update_fields=["_weighted_average"])
