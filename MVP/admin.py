from django.contrib import admin
from .models import MVP, Activity, ActivityType
# Register your models here.
admin.site.register(MVP)
admin.site.register(Activity)
admin.site.register(ActivityType)