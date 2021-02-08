from django.contrib import admin
from django.urls import path, include
from editorial.admin import editorial
from .views import *

urlpatterns = [
    path('', editorial.urls),
    path('site_login/', SiteLoginView.as_view(), name='site-login'),
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('doctor/membership/', DoctorView.as_view(), name='doctor-membership'),
    path('nurse/membership/', NurseView.as_view(), name='nurse-membership'),
    path('employee/membership/', EmployeeView.as_view(), name='employee-membership'),
    path('site_manager/membership/', SiteManagerView.as_view(), name='site-manager-membership'),
]
