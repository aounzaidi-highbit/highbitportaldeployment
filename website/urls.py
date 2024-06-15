from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('quarterly_evaluations', views.view_quarterly_valuations, name='quarterly_evaluations'),
    path("dashboard", views.dashboard, name="dashboard"),
    path("logout", views.logout_user, name="logout"),
    path("evaluation", views.evaluation_view, name="evaluation"),
    path('upload/', views.upload_file, name='upload_file'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('send-emails/', views.send_emails, name='send_emails'),
]
    