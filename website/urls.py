from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("logout", views.logout_user, name="logout"),
    path("evaluation", views.evaluation_view, name="evaluation"),
    # path('upload/', views.upload_file, name='upload_file'),
]
