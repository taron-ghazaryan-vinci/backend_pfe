from django.urls import path
from .views import CreateQuestionView, DeleteQuestionView, GetQuestionByIdView, GetAllQuestionsView, UpdateQuestionView

urlpatterns = [
    path('createQuestionTemplate/', CreateQuestionView.as_view(), name='create_question'),
    path('deleteOneQuestionTemplate/<str:question_id>/', DeleteQuestionView.as_view(), name='delete_question'),
    path('getOneQuestionTemplate/<str:question_id>/', GetQuestionByIdView.as_view(), name='get_question_by_id'),
    path('getAllQuestionsTemplate/', GetAllQuestionsView.as_view(), name='get_all_questions'),
    path('updateOneQuestionTemplate/<str:question_id>/', UpdateQuestionView.as_view(), name='update_question'),
]
