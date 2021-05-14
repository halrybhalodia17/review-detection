from django.contrib import admin
from django.urls import path
from . import views

# handler400 = 'review_detection_app.views.bad_request'
# handler403 = 'review_detection_app.views.bad_request'
# handler404 = 'review_detection_app.views.bad_request'
handler500 = 'review_detection_app.views.bad_request'

urlpatterns = [
   path('', views.geturl),
]