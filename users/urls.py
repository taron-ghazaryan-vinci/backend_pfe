from django.urls import path
from .views import (RegisterView, LoginView, SetTemplateTrueView,
                    GetAllUsersView, GetUserByIdView, GetUserResponsesView,
                    UpdateUserResponsesView, SetBooleanESGView, RemoveUserResponseIdView, RemoveUserEngagementIdView)

urlpatterns = [
    path('', GetAllUsersView.as_view(), name='get_all_users'),
    path('users/<str:user_id>/', GetUserByIdView.as_view(), name='get_user_by_id'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('set-template-true/<str:custom_id>/', SetTemplateTrueView.as_view(), name='set_template_true'),
    path('set-boolean-esg/<str:user_id>/', SetBooleanESGView.as_view(), name='set_boolean_esg'),
    path('user-responses/<str:email>/', GetUserResponsesView.as_view(), name='get-user-responses'),
    path('update-responses/', UpdateUserResponsesView.as_view(), name='update-user-responses'),
    path('remove-response-id/', RemoveUserResponseIdView.as_view(), name='remove_response_id'),

    path('remove-engagement-id/', RemoveUserEngagementIdView.as_view(), name='remove-engagement-id'),

]
