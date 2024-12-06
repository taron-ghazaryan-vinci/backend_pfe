from urllib import response
from django.shortcuts import render
from responsesTemplate.db import get_clients_responses, submit_client_response
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class SubmitClientResponseView(APIView):
    def post(self,request):

        data = request.data.get('responses',[])
        if not isinstance(data,list):
            return Response({"error":"les données doivent etre en liste"},status=400)
        
        for response in data:
            answer = response.get('answer')  
            company_id = response.get('company_id')  
            question_id = response.get('question_id')  
        
            if not answer or not company_id or not question_id:
                return Response({"error": "Réponse, ID de l'entreprise et ID de la question sont obligatoires."}, status=400)

            try:
                submit_client_response(answer, company_id, question_id)  # Appeler votre fonction MongoDB
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        
        return Response({"message":"toutes les reponses ont été enregistrée avec succès" }, status=201)


class GetClientResponsesView(APIView):
    def get(self, request, company_id):
        try:
            responses = get_clients_responses(company_id)  
            if not responses:
                return Response({"message": "Aucune réponse trouvée pour ce client."}, status=404)

            return Response({"responses": responses}, status=200)
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)