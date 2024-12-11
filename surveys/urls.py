from django.urls import path
from surveys.views import CreateSurveyView, GetEngagementsClientView, SubmitListQuestionsView, GlobalScoreView


urlpatterns = [
    path('create-survey/<str:company_email>/', CreateSurveyView.as_view(), name='create_survey'),
    path('engagements/<str:company_email>/', GetEngagementsClientView.as_view(), name='get_engagements'),
    path('submit-questions/<str:company_email>/', SubmitListQuestionsView.as_view(), name='submit_questions'),
    path('calculate-global-score/<str:company_email>/', GlobalScoreView.as_view(), name='calculate_global_score')
]
