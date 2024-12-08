from django.urls import path
from .views import RegisterView, LoginView, SetTemplateTrueView ,GetUserResponsesView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('set-template-true/<str:custom_id>/', SetTemplateTrueView.as_view(), name='set_template_true'),
    path('user-responses/<str:email>/', GetUserResponsesView.as_view(), name='get-user-responses'),
]
