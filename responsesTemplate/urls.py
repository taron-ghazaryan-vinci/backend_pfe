from django.urls import path

from .views import ClientResponseView, GetClientResponsesView, SubmitClientResponseView

urlpatterns = [
    path('responses/submit/', SubmitClientResponseView.as_view(), name='submit_response'),
    path('responses/<str:company_id>/', GetClientResponsesView.as_view(), name='get_client_responses'),  
    path('response/<int:company_id>/<int:question_id>/', ClientResponseView.as_view(), name='client_response'),

]
