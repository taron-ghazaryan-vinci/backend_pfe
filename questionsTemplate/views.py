from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from questionsTemplate.db import create_question, delete_question_by_id, get_all_questions, get_question_by_id, update_question_by_id

# Create your views here.
class CreateQuestionView(APIView):
    def post(self,request):
        question = request.data.get("question")   
        if not question:
            return Response({"error": "La question est obligatoire."}, status=400)
        
        try:
            create_question(question)
            return Response({"message" : "Question du onborading créé"}, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Erreur interne du serveur"}, status=500)

            
class DeleteQuestionView(APIView):
    def post(self,request,question_id):
        result = delete_question_by_id(question_id)
        if result.deleted_count == 0:
            return Response({"error": "Question introuvable"}, status=404)
        return Response({"message": "Question supprimée avec succès"}, status=200)


class GetQuestionByIdView(APIView):
    def get(self, request, question_id):
        question = get_question_by_id(question_id)
        if not question:
            return Response({"error": "Question introuvable"}, status=404)
        return Response({"question": question}, status=200)
        
        
class GetAllQuestionsView(APIView):
    def get(self, request):
        questions = get_all_questions()
        return Response({"questions": questions}, status=200)
       
        
class UpdateQuestionView(APIView):
    def put(self, request, question_id):
        new_question = request.data.get("question")
        result = update_question_by_id(question_id, new_question)
        if result.matched_count == 0:
            return Response({"error": "Question introuvable"}, status=404)
        return Response({"message": "Question mise à jour avec succès"}, status=200)
       