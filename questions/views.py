from django.shortcuts import render

from .db import (create_open_question, create_multiple_choice_question, delete_question_by_id,
                 update_question,get_all_questions)

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
            templates = data.get('templates')
            responses = data.get('responses', [])
            esg = data.get('esg')

            if not enjeu or not question_text or not templates or not responses or not esg:
                return Response(
                    {"error": "Tous les champs sont requis : enjeu, question, templates, responses, esg"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validation des réponses
            for response in responses:
                if not isinstance(response, dict) or 'label' not in response or 'scoreESG' not in response or 'scoreEngagement' not in response:
                    return Response(
                        {"error": "Chaque réponse doit contenir 'label', 'scoreESG' et 'scoreEngagement'"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Appeler la méthode pour créer la question
            question_id = create_multiple_choice_question(enjeu, question_text, templates, responses, esg)

            # Calcul du scoreTotal (sum(scoreESG) / 2)
            score_total = sum(resp.get('scoreESG', 0) for resp in responses) / 2

            # Récupérer les données de la question créée
            question_data = {
                "id": question_id,
                "enjeu": enjeu,
                "question": question_text,
                "templates": templates,
                "type": "choixMultiples",
                "responsesPossible": responses,
                "ESG": esg,
                "scoreTotal": round(score_total, 2)
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
            templates = data.get('templates')
            esg = data.get('esg')

            if not enjeu or not question_text or not templates or not esg:
                return Response(
                    {"error": "Tous les champs sont requis : enjeu, question, templates, esg"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Appeler la méthode pour créer la question
            question_id = create_open_question(enjeu, question_text, templates, esg)

            # Récupérer les données de la question créée
            question_data = {
                "id": question_id,
                "enjeu": enjeu,
                "question": question_text,
                "templates": templates,
                "type": "ouverte",
                "ESG": esg,
                "responsesPossible": [
                    {
                        "id": "1",
                        "label": None,  # Réponse initialement vide
                        "scoreESG": 0.00,
                        "scoreEngagement": 0.00
                    }
                ]
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


class UpdateQuestionView(APIView):
    def patch(self, request, question_id):
        """
        Endpoint pour mettre à jour une question par son ID.
        """
        try:
            updates = request.data  # Les données de mise à jour
            if not updates:
                return Response(
                    {"error": "Aucune donnée de mise à jour fournie."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Appeler la méthode pour mettre à jour la question
            is_updated = update_question(question_id, updates)
            if is_updated:
                return Response({"message": "Question mise à jour avec succès"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Question non trouvée ou aucune modification effectuée"},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetAllQuestionsView(APIView):
    def get(self, request):
        """
        Endpoint pour récupérer toutes les questions.
        """
        try:
            questions = get_all_questions()
            # Convertir ObjectId en string pour chaque question
            for question in questions:
                question['_id'] = str(question['_id'])
            return Response(questions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .db import get_question_by_id

class GetQuestionByIdView(APIView):
    def get(self, request, question_id):
        """
        Endpoint pour récupérer une question en fonction de son ID.
        """
        try:
            question = get_question_by_id(question_id)
            if question:
                return Response(
                    {"question": question},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Question introuvable"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


