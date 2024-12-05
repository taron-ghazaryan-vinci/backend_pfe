from urllib import response
from django.shortcuts import render
from rest_framework import status
from responsesTemplate.db import get_clients_responses, submit_client_response

# Create your views here.
class SubmitClientResponseView(APIView):
    def post(self,request):
        data = request.data
        answer = data.get('answer')  
        company_id = data.get('company_id')  
        question_id = data.get('question_id')  
    
        if not answer or not company_id or not question_id:
            return response({"error": "Réponse, ID de l'entreprise et ID de la question sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response_id = submit_client_response(answer, company_id, question_id)  # Appeler votre fonction MongoDB
            return response({"message": "Réponse enregistrée avec succès", "response_id": str(response_id)}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetClientResponsesView(APIView):
    def get(self, request, company_id):
        try:
            responses = get_clients_responses(company_id)  
            if not responses:
                return response({"message": "Aucune réponse trouvée pour ce client."}, status=status.HTTP_404_NOT_FOUND)

            return response({"responses": responses}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)