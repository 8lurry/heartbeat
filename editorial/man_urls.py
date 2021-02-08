from django.urls import path, include
from .man_views import *

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('schedule/create/', ScheduleCreateView.as_view(), name='create-schedule'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('schedule/update/<int:pk>/', ScheduleUpdateView.as_view(), name='update-schedule'),
    path('schedule/update/<int:pk>/token/create/', TokenCreateView.as_view(), name='create-token'),
    path('schedule/update/<int:pk>/token/record/keep/', HistoricalRecordCreateView.as_view(), name='record-keep'),
    path('schedule/update/<int:pk>/token/', TokenView.as_view(), name='token'),
    path('schedule/token/view/<int:pk>/doc/up/', HistoricalRecordCreateView.as_view(), name='doc-upload')
]