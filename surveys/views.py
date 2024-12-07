from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from surveys.db import create_survey

# Create your views here.
class CreateSurveyView(APIView):
    def get(self, request, company_email):
        survey = create_survey(company_email)

        if 'error' in survey:
            return Response({"error": survey["error"]}, status=400)
        
        return Response(survey,status=200)

