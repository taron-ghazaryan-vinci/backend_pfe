from django.urls import path
from surveys.views import CreateSurveyView, GetEngagementsClient

urlpatterns = [
    path('create-survey/<str:company_email>/', CreateSurveyView.as_view(), name='create_survey'),
    path('engagements/<str:company_email>/', GetEngagementsClient.as_view(), name='get_engagements'),
]
