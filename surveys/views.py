from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from surveys.db import create_survey, get_engagements_clients
from users.db import find_user_by_email

# Create your views here.
class CreateSurveyView(APIView):
    def get(self, request, company_email):
        survey = create_survey(company_email)

        if 'error' in survey:
            return Response({"error": survey["error"]}, status=400)
        
        return Response(survey,status=200)

class GetEngagementsClientView(APIView):
    def get(self,request,company_email):
        company = find_user_by_email(company_email)
        if not company:
            return Response({"error": "Company not found"}, status=404)
       
        result = get_engagements_clients(company_email)
        if 'error' in result:
            return Response(result, status=404)  
        
        engagements = result.get("engagements", [])
        return Response({"engagements": engagements}, status=200)