from django.shortcuts import render

from .db import create_open_question, create_multiple_choice_question, delete_question_by_id

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class CreateMultipleChoiceQuestionView(APIView):
    def post(self, request):
        """
        Endpoint pour créer une question de type choixMultiple.
        """
        data = request.data
        try:
            # Validation des données
            enjeu = data.get('enjeu')
            question_text = data.get('question')
            templates = data.get('templates', [])
            responses = data.get('responses', [])

            if not enjeu or not question_text or not templates or not responses:
                return Response(
                    {"error": "Tous les champs sont requis : enjeu, question, templates, responses"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Appeler la méthode pour créer la question
            question_id = create_multiple_choice_question(enjeu, question_text, templates, responses)

            # Récupérer les données de la question créée
            question_data = {
                "id": str(question_id),
                "enjeu": enjeu,
                "question": question_text,
                "templates": templates,
                "responsesPossible": [
                    {"id": str(i + 1), "label": response, "scoreESG": None, "scoreEngagement": None}
                    for i, response in enumerate(responses)
                ],
                "type": "choixMultiples"
            }

            return Response(
                {"message": "Question créée avec succès", "question": question_data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateOpenQuestionView(APIView):
    def post(self, request):
        """
        Endpoint pour créer une question de type ouverte.
        """
        data = request.data
        try:
            # Validation des données
            enjeu = data.get('enjeu')
            question_text = data.get('question')
            templates = data.get('templates', [])

            if not enjeu or not question_text or not templates:
                return Response(
                    {"error": "Tous les champs sont requis : enjeu, question, templates"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Appeler la méthode pour créer la question
            question_id = create_open_question(enjeu, question_text, templates)

            # Récupérer les données de la question créée
            question_data = {
                "id": str(question_id),
                "enjeu": enjeu,
                "question": question_text,
                "templates": templates,
                "responsesPossible": [],
                "type": "ouverte"
            }

            return Response(
                {"message": "Question créée avec succès", "question": question_data},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteQuestionView(APIView):
    def delete(self, request, question_id):
        """
        Endpoint pour supprimer une question par son ID.
        """
        try:
            is_deleted = delete_question_by_id(question_id)
            if is_deleted:
                return Response({"message": "Question supprimée avec succès"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Question non trouvée"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

