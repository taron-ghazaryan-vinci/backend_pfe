from django.urls import path
from .views import CreateMultipleChoiceQuestionView, CreateOpenQuestionView, DeleteQuestionView

urlpatterns = [
    path('create-multiple-choice/', CreateMultipleChoiceQuestionView.as_view(), name='create_multiple_choice'),
    path('create-open/', CreateOpenQuestionView.as_view(), name='create_open'),
    path('delete-question/<str:question_id>/', DeleteQuestionView.as_view(), name='delete-question')
]
