from django.urls import path
from .views import (CreateMultipleChoiceQuestionView, CreateOpenQuestionView,
                    DeleteQuestionView, UpdateQuestionView, GetAllQuestionsView, GetQuestionByIdView)

urlpatterns = [
    path('', GetAllQuestionsView.as_view(), name='get-all-questions'),
    path('question/<str:question_id>/', GetQuestionByIdView.as_view(), name='get_question_by_id'),
    path('create-multiple-choice/', CreateMultipleChoiceQuestionView.as_view(), name='create_multiple_choice'),
    path('create-open/', CreateOpenQuestionView.as_view(), name='create_open'),
    path('delete-question/<str:question_id>/', DeleteQuestionView.as_view(), name='delete-question'),
    path('update-question/<str:question_id>/', UpdateQuestionView.as_view(), name='update-question')
]
