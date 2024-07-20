import datetime
from django.db import models
from website.models import Teams, Employee

class MVP(models.Model):
    name = models.CharField(max_length=100)
    plan=models.TextField(null=True, blank=True)
    team_name=models.ForeignKey(Teams,on_delete=models.CASCADE)        
    updated_by=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True)
    start_date = models.DateField()
    status = models.CharField(max_length=100,choices=[('Pause', 'Pause'), ('Completed', 'Completed'), ('Active','Active')],default='Active')
    end_date = models.DateField(null=True, blank=True)
    current_phase = models.CharField(max_length=100,choices=[('MVP', 'MVP'), ('Product', 'Product'),('Failed','Failed')],default='MVP')
    developers = models.ManyToManyField(Employee, related_name='developers')
    planners = models.ManyToManyField(Employee, related_name='planners')
    associates = models.ManyToManyField(Employee, related_name='associates')
    development_starting_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    first_completion_date=models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            previous = MVP.objects.get(pk=self.pk)
            changes = []
            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(previous, field_name)
                new_value = getattr(self, field_name)

                if old_value is None:
                    if old_value != new_value:
                        changes.append(f'{field.verbose_name}: set to "{new_value}" updated by "{self.updated_by.employee_name}"')
                else:
                    if old_value != new_value:
                        changes.append(f'{field.verbose_name}: changed from "{old_value}" to "{new_value}" updated by "{self.updated_by.employee_name}"')
            if changes:
                notes = "\n".join(changes)
                activity = Activity(
                    mvp=self,
                    activity_type=ActivityType.objects.get_or_create(name="Update")[0],
                    team_name=self.team_name,
                    notes=notes,
                )
                activity.save()

        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "MVP"
        verbose_name_plural = "MVPs"

class ActivityType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Activity Type"  
        verbose_name_plural = "Activity Types"
    
class Activity(models.Model):
    mvp = models.ForeignKey(MVP,on_delete=models.CASCADE)
    activity_type = models.ForeignKey(ActivityType,on_delete=models.CASCADE)
    team_name=models.ForeignKey(Teams,on_delete=models.CASCADE,null=True)
    notes=models.TextField()
    created_at=models.DateField(auto_now_add=True)
    created_by=models.ForeignKey(Employee,on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.mvp.name
    def save(self, *args, **kwargs):
        if self.mvp and self.mvp.team_name:
            self.team_name = self.mvp.team_name
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
