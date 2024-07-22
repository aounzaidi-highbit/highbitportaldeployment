from django.urls import path
from MVP.views import product_list
from . import views
from website import views  as v2
urlpatterns=[
    path('', v2.home, name='home'),
    path('mvp-form/<str:phase>/', views.mvp_form, name='mvp_form'),
    path('mvp-list/', views.mvp_list, name='mvp_list'),
    path('product-list/', views.product_list, name='product_list'),
    path('mvp-edit/<int:pk>/', views.edit_mvp, name='edit_mvp'),
    path('activity-form/', views.activity_form, name='activity_form'),
    path('activity-list/', views.activity_list, name='activity_list'),
    path('activity-type-form', views.add_activity_type, name='activity_type_form'),
    path('archive_mvp/<int:pk>/', views.archive_mvp, name='archive_mvp'),
    path('archive-list/', views.archive_list, name='archive_list'),
    path('unarchive_mvp/<int:pk>/', views.unarchive_mvp, name='unarchive_mvp'),
    path('activity-type-list/', views.activity_types_list, name='activity_type_list'),
    path('edit-activity-type/<int:pk>/', views.edit_activity_type, name='edit_activity'),  
    path('failed-list/', views.failed_mvp_list, name='failed_mvp_list'),
    path('product_form/<str:phase>/', views.product_form, name='product_form'),
    path('failed-form/<str:phase>/', views.failed_form, name='failed_form'),
    path('short-update-form/', views.short_update_form, name='short_update_form'),
    path('short-update-list/', views.short_update_list, name='short_update_list'),
    path('edit-short-update/<int:pk>/', views.edit_short_update, name='edit_short_update'),
]

