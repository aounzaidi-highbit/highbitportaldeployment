from django.urls import path
from MVP.views import product_list
from . import views
from website import views  as v2
urlpatterns=[
    path('', v2.home, name='home'),
    path('mvp-form/', views.mvp_form, name='mvp_form'),
    path('mvp-list/', views.mvp_list, name='mvp_list'),
    path('product-list/', views.product_list, name='product_list'),
    path('mvp-edit/<int:pk>/', views.edit_mvp, name='edit_mvp'),
    path('activity-form/', views.activity_form, name='activity_form'),
    path('activity-list/', views.activity_list, name='activity_list'),
    path('activity-type-form', views.add_activity_type, name='activity_type_form'),
]
