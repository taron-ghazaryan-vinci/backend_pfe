from django.urls import path
from surveys.views import createSurveyView

urlpatterns = [
    path('create-survey/<str:company_email>/', CreateSurveyView.as_view(), name='create_survey'),
]
