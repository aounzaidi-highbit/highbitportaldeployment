from django.db import models
from website.models import Teams, Employee

class MVP(models.Model):
    name = models.TextField()
    team_name=models.ForeignKey(Teams,on_delete=models.CASCADE)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    end_date = models.DateField(null=True, blank=True)
    current_phase = models.CharField(max_length=100,choices=[('MVP', 'MVP'), ('Product', 'Product')])
    developers = models.ManyToManyField(Employee, related_name='developers')
    planners = models.ManyToManyField(Employee, related_name='planners')
    created_at = models.DateField(auto_now_add=True,null=True)
    
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
    notes=models.TextField()
    created_at=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.mvp.name
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"