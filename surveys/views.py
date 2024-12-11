from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from surveys.db import create_survey, get_engagements_clients, submit_one_question, calculate_global_score
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

class SubmitListQuestionsView(APIView):
    def post(self, request, company_email):
        # Rechercher l'entreprise par email
        company = find_user_by_email(company_email)
        if not company:
            return Response({"error": "Company not found"}, status=404)

        if company.get("role") != "client":
            return Response({"error": "Only clients can submit responses"},
                            status=403)

        # Vérifier les données envoyées
        data = request.data
        if not data or not isinstance(data,
                                      list):  # Vérifier si c'est une liste
            return Response({"error": "Data must be a list of objects"},
                            status=400)

        # Parcourir chaque objet de la liste
        for item in data:
            # Valider les champs requis
            question_id = item.get("questionId")
            responses = item.get("responsesChosen")
            engagements = item.get("engagementsChosen")
            free_text = item.get(
                "freeText")  # Ajouter la récupération du champ de texte libre

            if not question_id or (
                not responses and not engagements and not free_text):
                return Response(
                    {"error": f"Missing data for question: {item}"},
                    status=400
                )

            # Soumettre une question
            submit_one_question(company_email, question_id, responses,
                                engagements, free_text)

        return Response({"message": "Responses submitted successfully"},
                        status=200)


class GlobalScoreView(APIView):
    def get(self, request, company_email):
        try:
            scores = calculate_global_score(company_email)
            if "error" in scores:
                return Response(
                    {"success": False, "error": scores["error"]}, status=404)

            return Response({"success": True, "data": scores})
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)
