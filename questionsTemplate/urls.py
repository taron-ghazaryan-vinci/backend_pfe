from django.urls import path
from .views import CreateQuestionView, DeleteQuestionView, GetQuestionByIdView, GetAllQuestionsView, UpdateQuestionView

urlpatterns = [
    path('create/', CreateQuestionView.as_view(), name='create_question'),
    path('delete/<str:question_id>/', DeleteQuestionView.as_view(), name='delete_question'),
    path('get/<str:question_id>/', GetQuestionByIdView.as_view(), name='get_question_by_id'),
    path('all/', GetAllQuestionsView.as_view(), name='get_all_questions'),
    path('update/<str:question_id>/', UpdateQuestionView.as_view(), name='update_question'),
]
