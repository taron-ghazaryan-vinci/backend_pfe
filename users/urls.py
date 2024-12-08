from django.urls import path
from .views import RegisterView, LoginView, GetUserResponsesView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('user-responses/<str:email>/', GetUserResponsesView.as_view(), name='get-user-responses'),
]