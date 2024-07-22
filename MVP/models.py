import datetime
from django.db import models
from website.models import Teams, Employee

class MVP(models.Model):
    name = models.CharField(max_length=100)
    plan=models.TextField(null=True, blank=True)
    team_name=models.ForeignKey(Teams,on_delete=models.CASCADE)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_mvps',null=True)
    updated_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='updated_mvps',null=True)
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
    notes=models.TextField(null=True, blank=True)
    changes=models.TextField(null=True, blank=True)
    created_at=models.DateField(auto_now_add=True)
    remarks=models.TextField(null=True, blank=True)
    created_by=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.mvp.name
    def save(self, *args, **kwargs):
        if self.mvp and self.mvp.team_name:
            self.team_name = self.mvp.team_name
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

class ShortUpdate(models.Model):
    team=models.ForeignKey(Teams,on_delete=models.CASCADE)
    status=models.CharField(max_length=100, choices=[('Success','Success'),('Fail','Fail'),('Pending','Pending')])
    title=models.CharField(max_length=255)
    description=models.TextField()
    start_date=models.DateField()
    end_date=models.DateField(null=True, blank=True)
    created_at=models.DateField(auto_now_add=True)
    created_by=models.ForeignKey(Employee,on_delete=models.CASCADE,null=True)
    
    class Meta:
        verbose_name = "Short Update"
        verbose_name_plural = "Short Updates"
    def __str__(self) -> str:
        return self.title