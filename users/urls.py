from django.urls import path
from .views import RegisterView, LoginView, SetTemplateTrueView, GetAllUsersView, GetUserByIdView, GetUserResponsesView

urlpatterns = [
    path('', GetAllUsersView.as_view(), name='get_all_users'),
    path('<str:user_id>/', GetUserByIdView.as_view(), name='get_user_by_id'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('set-template-true/<str:custom_id>/', SetTemplateTrueView.as_view(), name='set_template_true'),
    path('user-responses/<str:email>/', GetUserResponsesView.as_view(), name='get-user-responses'),
]
